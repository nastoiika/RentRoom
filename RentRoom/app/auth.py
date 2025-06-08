from functools import wraps
from flask import Blueprint, request,  render_template, abort, request, make_response, session, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from app import db
from datetime import datetime
from .models import Users, Advertisement, Bookings
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint('auth', __name__, url_prefix='/auth')

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Необходимо авторизоваться'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@bp.route('/login',  methods=['GET', 'POST'])
def auth():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        user = Users.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            return render_template('auth.html')
    return render_template('auth.html')

@bp.route('/registration', methods=['GET', 'POST'])
def registr():
    if request.method == "POST":
        try:
            hash = generate_password_hash(request.form['password'])
            user = Users(
                username=request.form['username'],
                password=hash,
                email = request.form['email']
            )
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print("Ошибка добавления в БД:", e)
        return redirect(url_for('auth'))
    return render_template('registr.html')

@bp.errorhandler(404)
def page_not_found(error):
    return render_template('errorpage.html')

@bp.errorhandler(401)
def unauthorized(error):
    return render_template('errorpage.html')

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
