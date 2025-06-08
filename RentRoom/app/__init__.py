from flask import Flask
from sqlalchemy.exc import SQLAlchemyError
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
import os
from flask_login import current_user 
from .db import db

def handle_sqlalchemy_error(err):
    error_msg = ('Возникла ошибка при подключении к базе данных. '
                 'Повторите попытку позже.')
    return f'{error_msg} (Подробнее: {err})', 500

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_pyfile('config.py', silent=False)
    app.config['DEBUG'] = True
    
    login_manager = LoginManager(app)
    db.init_app(app)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    from . import auth
    app.register_blueprint(auth.bp)
    auth.login_manager.init_app(app)

    from . import users
    app.register_blueprint(users.bp)
    app.route('/', endpoint='index')(users.index)

    from . import admin
    app.register_blueprint(admin.bp)

    return app