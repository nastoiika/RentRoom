from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from app import db
from datetime import datetime

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
 
    def __get_id__(self):
        return self.id

class Advertisement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(125), nullable=False) #Имя владельца
    roomtype = db.Column(db.String(25), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(125), nullable=False)
    city = db.Column(db.String(125), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    img = db.Column(db.String(125), nullable=False)

class Bookings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_begin = db.Column(db.DateTime, default=datetime.utcnow)
    date_end = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    advertisement_id = db.Column(db.Integer, db.ForeignKey('advertisement.id'), nullable=False)

    user = db.relationship('Users', backref=db.backref('bookings', lazy=True))
    advertisement = db.relationship('Advertisement', backref=db.backref('bookings', lazy=True))
