from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import Integer


class Urls(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500))
    shorten_url = db.Column(db.String(500))
    creation_date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    reg_date = db.Column(db.DateTime(timezone=True), default=func.now())
    urls = db.relationship('Urls')

class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    reg_date = db.Column(db.DateTime(timezone=True), default=func.now())


class url_analytics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ipaddress = db.Column(db.String(150))
    city = db.Column(db.String(150))
    country = db.Column(db.String(150))
    click_date = db.Column(db.DateTime(timezone=True), default=func.now())
    url_id = db.Column(db.Integer, db.ForeignKey('urls.id'))

class click_counts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    click_num = db.Column(Integer)
    url_id = db.Column(db.Integer, db.ForeignKey('urls.id'))