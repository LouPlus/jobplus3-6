#!/usr/bin/env python3
# encoding: utf-8

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from flask_login import UserMixin

db = SQLAlchemy()


class Base(db.Model):
    __abstract__ = True
    created_at = db.Column(db.DateTime, default=datetime.utcnow, )
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow())


class User(Base):

    __tablename__ = 'user'

    ROLE_ADMIN = 10
    ROLE_SEEKER = 20
    ROLE_COMPANY = 30

    STATUS_NORMAL = 0
    STATUS_SUSPENDED = -1

    id = db.Column(db.Integer, primarykey=True)
    username = db.Column(db.String(32), unique=True, index=True, nullable=False)
    email = db.Column(db.String(64), unique=True, index=True, nullable=False)
    _password = db.Column('password', db.String(256), nullable=False)
    role = db.Column(db.SmallInteger, default=ROLE_SEEKER)
    status = db.Column(db.SmallInteger, default=STATUS_NORMAL)

class Seeker(Base):

    __tablename__ = 'seeker'

    id = db.Column(db.Integer, primarykey=True)
    user_id = db.Column(db.ForeignKey('user.id'))