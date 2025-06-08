import os
import random
from ssl import SSLSession
from flask import Blueprint, request,  render_template, abort, request, make_response, session, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from .db import db
from .models import Users, Advertisement, Bookings
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, date
from sqlalchemy import and_, or_
from functools import wraps
from datetime import datetime, time

bp = Blueprint('users', __name__, url_prefix='/users')

login_manager = LoginManager()
login_manager.login_view = 'users.index'
login_manager.login_message = 'Необходимо авторизоваться'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@bp.route('/', methods=['GET', 'POST'])
def index():
    query = Advertisement.query
    if request.method in ['GET', 'POST']:
        form_data = request.args if request.method == 'GET' else request.form
        
        roomtype = form_data.get('roomtype')
        price_max = form_data.get('price_max')
        capacity = form_data.get('capacity')
        city = form_data.get('city')
        date_start = form_data.get('date_start')
        date_end = form_data.get('date_end')

        if roomtype:
            query = query.filter(Advertisement.roomtype == roomtype)
        if price_max:
            query = query.filter(Advertisement.price <= int(price_max))
        if capacity:
            query = query.filter(Advertisement.capacity >= int(capacity))
        if city:
            query = query.filter(Advertisement.city == city)

        if date_start and date_end:
            try:
                start = datetime.combine(datetime.strptime(date_start, '%Y-%m-%d').date(), time.min)
                end = datetime.combine(datetime.strptime(date_end, '%Y-%m-%d').date(), time.max)
                
                busy_ads = db.session.query(Bookings.advertisement_id).filter(
                    or_(
                        and_(Bookings.date_begin <= start, Bookings.date_end >= start),
                        and_(Bookings.date_begin <= end, Bookings.date_end >= end),
                        and_(Bookings.date_begin >= start, Bookings.date_end <= end),
                    )
                ).subquery()

                query = query.filter(Advertisement.id.notin_(busy_ads))
            except ValueError:
                pass

    advertisement = query.all()
    return render_template(
        'index.html',
        advertisement=advertisement,
        form_data={
            'roomtype': request.args.get('roomtype', ''),
            'price_max': request.args.get('price_max', ''),
            'capacity': request.args.get('capacity', ''),
            'city': request.args.get('city', ''),
            'date_start': request.args.get('date_start', ''),
            'date_end': request.args.get('date_end', '')
        }
    )

@bp.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    bookings = Bookings.query.filter_by(user_id=user_id).all()
    return render_template('profile.html', bookings=bookings)

@bp.route('/booking/<int:room_id>', methods=['GET', 'POST'])
@login_required
def booking(room_id):
    room = Advertisement.query.get_or_404(room_id)
    today = date.today().isoformat()
    if request.method == 'POST':
        date_begin = request.form['date_begin']
        date_end = request.form['date_end']

        if date_begin and date_end:
            try:
                start = datetime.strptime(date_begin, '%Y-%m-%d')
                end = datetime.strptime(date_end, '%Y-%m-%d')

                conflict = Bookings.query.filter(
                    Bookings.advertisement_id == room_id,
                    or_(
                        and_(Bookings.date_begin <= start, Bookings.date_end >= start),
                        and_(Bookings.date_begin <= end, Bookings.date_end >= end),
                        and_(Bookings.date_begin >= start, Bookings.date_end <= end)
                    )
                ).first()

                if conflict:
                    flash('Выбранные даты уже заняты, пожалуйста, выберите другие.', 'error')
                    return render_template('booking.html', room=room)

                new_booking = Bookings(
                    date_begin=start,
                    date_end=end,
                    user_id=current_user.id,
                    advertisement_id=room_id
                )
                db.session.add(new_booking)
                db.session.commit()
                flash('Бронирование успешно создано!', 'success')
                return redirect(url_for('index'))

            except ValueError:
                flash('Некорректный формат даты.', 'error')
                return render_template('booking.html', room=room)
        else:
            flash('Пожалуйста, выберите даты.', 'error')
            return render_template('booking.html', room=room)

    return render_template('booking.html', room=room, today=today)

@bp.route('/delete_booking/<int:booking_id>', methods=['POST'])
@login_required
def delete_booking(booking_id):
    booking = Bookings.query.get_or_404(booking_id)
    db.session.delete(booking)
    db.session.commit()
    return redirect(url_for('profile', user_id=current_user.id))