import os
import random
from ssl import SSLSession
from flask import Blueprint, request,  render_template, abort, request, make_response, session, redirect, url_for, flash, current_app
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from .db import db
from .models import Users, Advertisement, Bookings
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, date
from sqlalchemy import and_, or_
from functools import wraps
from datetime import datetime, time

bp = Blueprint('admin', __name__, url_prefix='/admin')

login_manager = LoginManager()
login_manager.login_view = 'users.index'
login_manager.login_message = 'Необходимо авторизоваться'
login_manager.login_message_category = 'warning'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
UPLOAD_FOLDER = 'static/uploads'

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/add_room', methods=['GET', 'POST'])
@admin_required
def add_room():
    if request.method == 'POST':
        if 'img' not in request.files:
            flash('Файл не был загружен')
            return redirect(request.url)
            
        file = request.files['img']
        if file.filename == '':
            flash('Не выбран файл для загрузки')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
    
            new_room = Advertisement(
                name=request.form['name'],
                roomtype=request.form['roomtype'],
                price=int(request.form['price']),
                capacity=int(request.form['capacity']),
                address=request.form['address'],
                city=request.form['city'],
                img=filename,
                created_at=datetime.utcnow()
            )
            db.session.add(new_room)
            db.session.commit()
            
            flash('Помещение успешно добавлено!', 'success')
            return redirect(url_for('index'))
            
        flash('Недопустимый формат файла. Разрешены: PNG, JPG, JPEG, GIF', 'error')
    return render_template('add_room.html')

@bp.route('/delete_room/<int:room_id>', methods=['POST'])
@admin_required
def delete_room(room_id):
    room = Advertisement.query.get_or_404(room_id)
    
    img_path = os.path.join(current_app.root_path, 'static/uploads', room.img)
    if os.path.exists(img_path):
        os.remove(img_path)

    db.session.delete(room)
    db.session.commit()
    return redirect(url_for('rooms'))

@bp.route('/edit_room/<int:room_id>', methods=['GET', 'POST'])
@admin_required
def edit_room(room_id):
    room = Advertisement.query.get_or_404(room_id)

    if request.method == 'POST':
        room.name = request.form['name']
        room.roomtype = request.form['roomtype']
        room.price = request.form['price']
        room.capacity = request.form['capacity']
        room.address = request.form['address']
        room.city = request.form['city']

        img = request.files.get('img')
        if img and img.filename:
            filename = secure_filename(img.filename)
            img.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            room.img = filename

        db.session.commit()
        return redirect(url_for('rooms'))

    return render_template('edit_room.html', room=room)

@bp.route('/rooms')
@admin_required
def rooms():
    advertisement = Advertisement.query.all()
    return render_template('rooms.html', advertisement=advertisement)

@bp.route('/bookings')
@admin_required
def bookings():
    bookings = Bookings.query.all()
    return render_template('bookings.html', bookings=bookings)