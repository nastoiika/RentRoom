import os
import random
from ssl import SSLSession
from flask import Flask, flash, render_template, abort, request, make_response, session, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from db import db
from models import Users, Advertisement, Bookings
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, date
from sqlalchemy import and_, or_
from functools import wraps
from datetime import datetime, time

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
UPLOAD_FOLDER = 'static/uploads'

app = Flask(__name__)
app.config.from_pyfile('config.py', silent=False)

login_manager = LoginManager(app)
db.init_app(app)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     query = Advertisement.query
#     if request.method in ['GET', 'POST']:
#         form_data = request.args if request.method == 'GET' else request.form
        
#         roomtype = form_data.get('roomtype')
#         price_max = form_data.get('price_max')
#         capacity = form_data.get('capacity')
#         city = form_data.get('city')
#         date_start = form_data.get('date_start')
#         date_end = form_data.get('date_end')

#         if roomtype:
#             query = query.filter(Advertisement.roomtype == roomtype)
#         if price_max:
#             query = query.filter(Advertisement.price <= int(price_max))
#         if capacity:
#             query = query.filter(Advertisement.capacity >= int(capacity))
#         if city:
#             query = query.filter(Advertisement.city == city)

#         if date_start and date_end:
#             try:
#                 start = datetime.combine(datetime.strptime(date_start, '%Y-%m-%d').date(), time.min)
#                 end = datetime.combine(datetime.strptime(date_end, '%Y-%m-%d').date(), time.max)
                
#                 busy_ads = db.session.query(Bookings.advertisement_id).filter(
#                     or_(
#                         and_(Bookings.date_begin <= start, Bookings.date_end >= start),
#                         and_(Bookings.date_begin <= end, Bookings.date_end >= end),
#                         and_(Bookings.date_begin >= start, Bookings.date_end <= end),
#                     )
#                 ).subquery()

#                 query = query.filter(Advertisement.id.notin_(busy_ads))
#             except ValueError:
#                 pass

#     advertisement = query.all()
#     return render_template(
#         'index.html',
#         advertisement=advertisement,
#         form_data={
#             'roomtype': request.args.get('roomtype', ''),
#             'price_max': request.args.get('price_max', ''),
#             'capacity': request.args.get('capacity', ''),
#             'city': request.args.get('city', ''),
#             'date_start': request.args.get('date_start', ''),
#             'date_end': request.args.get('date_end', '')
#         }
#     )

# @app.route('/profile/<int:user_id>')
# @login_required
# def profile(user_id):
#     bookings = Bookings.query.filter_by(user_id=user_id).all()
#     return render_template('profile.html', bookings=bookings)

# @app.route('/bookings')
# @admin_required
# def bookings():
#     bookings = Bookings.query.all()
#     return render_template('bookings.html', bookings=bookings)

# @app.route('/auth',  methods=['GET', 'POST'])
# def auth():
#     if request.method == "POST":
#         username = request.form['username']
#         password = request.form['password']
#         user = Users.query.filter_by(username=username).first()
#         if user and check_password_hash(user.password, password):
#             login_user(user)
#             return redirect(url_for('index'))
#         else:
#             return render_template('auth.html')
#     return render_template('auth.html')

# @app.route('/registration', methods=['GET', 'POST'])
# def registr():
#     if request.method == "POST":
#         try:
#             hash = generate_password_hash(request.form['password'])
#             user = Users(
#                 username=request.form['username'],
#                 password=hash,
#                 email = request.form['email']
#             )
#             db.session.add(user)
#             db.session.commit()
#         except Exception as e:
#             db.session.rollback()
#             print("Ошибка добавления в БД:", e)
#         return redirect(url_for('auth'))
#     return render_template('registr.html')

# @app.errorhandler(404)
# def pageNotFound(error):
#     return render_template('errorpage.html')

# @app.errorhandler(401)
# def unauthorized(error):
#     return render_template('errorpage.html')

# @app.route('/logout')
# def logout():
#     logout_user()
#     return redirect(url_for('index'))

# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @app.route('/add_room', methods=['GET', 'POST'])
# @admin_required
# def add_room():
#     if request.method == 'POST':
#         if 'img' not in request.files:
#             flash('Файл не был загружен')
#             return redirect(request.url)
            
#         file = request.files['img']
#         if file.filename == '':
#             flash('Не выбран файл для загрузки')
#             return redirect(request.url)
            
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             filepath = os.path.join(UPLOAD_FOLDER, filename)
#             file.save(filepath)
    
#             new_room = Advertisement(
#                 name=request.form['name'],
#                 roomtype=request.form['roomtype'],
#                 price=int(request.form['price']),
#                 capacity=int(request.form['capacity']),
#                 address=request.form['address'],
#                 city=request.form['city'],
#                 img=filename,
#                 created_at=datetime.utcnow()
#             )
#             db.session.add(new_room)
#             db.session.commit()
            
#             flash('Помещение успешно добавлено!', 'success')
#             return redirect(url_for('index'))
            
#         flash('Недопустимый формат файла. Разрешены: PNG, JPG, JPEG, GIF', 'error')
#     return render_template('add_room.html')

# @app.route('/delete_room/<int:room_id>', methods=['POST'])
# @admin_required
# def delete_room(room_id):
#     room = Advertisement.query.get_or_404(room_id)
    
#     img_path = os.path.join(app.root_path, 'static/uploads', room.img)
#     if os.path.exists(img_path):
#         os.remove(img_path)

#     db.session.delete(room)
#     db.session.commit()
#     return redirect(url_for('rooms'))

# @app.route('/edit_room/<int:room_id>', methods=['GET', 'POST'])
# @admin_required
# def edit_room(room_id):
#     room = Advertisement.query.get_or_404(room_id)

#     if request.method == 'POST':
#         room.name = request.form['name']
#         room.roomtype = request.form['roomtype']
#         room.price = request.form['price']
#         room.capacity = request.form['capacity']
#         room.address = request.form['address']
#         room.city = request.form['city']

#         img = request.files.get('img')
#         if img and img.filename:
#             filename = secure_filename(img.filename)
#             img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#             room.img = filename

#         db.session.commit()
#         return redirect(url_for('rooms'))

#     return render_template('edit_room.html', room=room)

# @app.route('/rooms')
# @admin_required
# def rooms():
#     advertisement = Advertisement.query.all()
#     return render_template('rooms.html', advertisement=advertisement)

# @app.route('/booking/<int:room_id>', methods=['GET', 'POST'])
# @login_required
# def booking(room_id):
#     room = Advertisement.query.get_or_404(room_id)
#     today = date.today().isoformat()
#     if request.method == 'POST':
#         date_begin = request.form['date_begin']
#         date_end = request.form['date_end']

#         if date_begin and date_end:
#             try:
#                 start = datetime.strptime(date_begin, '%Y-%m-%d')
#                 end = datetime.strptime(date_end, '%Y-%m-%d')

#                 conflict = Bookings.query.filter(
#                     Bookings.advertisement_id == room_id,
#                     or_(
#                         and_(Bookings.date_begin <= start, Bookings.date_end >= start),
#                         and_(Bookings.date_begin <= end, Bookings.date_end >= end),
#                         and_(Bookings.date_begin >= start, Bookings.date_end <= end)
#                     )
#                 ).first()

#                 if conflict:
#                     flash('Выбранные даты уже заняты, пожалуйста, выберите другие.', 'error')
#                     return render_template('booking.html', room=room)

#                 new_booking = Bookings(
#                     date_begin=start,
#                     date_end=end,
#                     user_id=current_user.id,
#                     advertisement_id=room_id
#                 )
#                 db.session.add(new_booking)
#                 db.session.commit()
#                 flash('Бронирование успешно создано!', 'success')
#                 return redirect(url_for('index'))

#             except ValueError:
#                 flash('Некорректный формат даты.', 'error')
#                 return render_template('booking.html', room=room)
#         else:
#             flash('Пожалуйста, выберите даты.', 'error')
#             return render_template('booking.html', room=room)

#     return render_template('booking.html', room=room, today=today)

# @app.route('/delete_booking/<int:booking_id>', methods=['POST'])
# @login_required
# def delete_booking(booking_id):
#     booking = Bookings.query.get_or_404(booking_id)
#     db.session.delete(booking)
#     db.session.commit()
#     return redirect(url_for('profile', user_id=current_user.id))

# if __name__ == '__main__':
#     app.run(debug=True)