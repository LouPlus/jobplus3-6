#!/usr/bin/env python3
# encoding: utf-8

import datetime
import re

from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_uploads import configure_uploads, patch_request_class

from jobplus.config import configs
from jobplus.models import db, User
from jobplus.forms import photos


def register_filters(app):

    @app.template_filter()
    def timesince(value):
        now = datetime.datetime.utcnow()
        delta = now - value
        if delta.days > 365:
            return '{}年前'.format(delta.days // 365)
        if delta.days > 30:
            return '{}月前'.format(delta.days//30)
        if delta.days > 0:
            return '{}天前'.format(delta.days)
        if delta.seconds > 3600:
            return '{}小时前'.format(delta.seconds // 3600)
        if delta.seconds > 60:
            return '{}分钟前'.format(delta.seconds // 60)
        return '刚刚'
    
    @app.template_filter()
    def date_format(found_date):
        date = datetime.datetime.strftime(found_date, '%Y')
        return date
    
    @app.template_filter()
    def scale_format(scale):
        if scale == 0:
            return '1-15名雇员'
        elif scale == 1:
            return '15-50名雇员'
        elif scale == 2:
            return '50-150名雇员'
        elif scale == 3:
            return '150-500名雇员'
        else:
            return '500+雇员'
    
    @app.template_filter()
    def sentence_split(sentence):
        return re.split(r",|\.|;|，|；|、|\s|/|\\", sentence)

    @app.template_filter()
    def ex_link(url):
        url = str(url)
        if 'http://' in url or 'https' in url:
            return url
        else:
            return "http://" + str(url)


def register_blueprints(app):
    from .handlers import front, company, job, seeker, admin

    app.register_blueprint(front)
    app.register_blueprint(company)
    app.register_blueprint(job)
    app.register_blueprint(seeker)
    app.register_blueprint(admin)


def register_extensions(app):
    db.init_app(app)
    Migrate(app, db)

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def user_loader(id):
        return User.query.get(id)

    login_manager.login_view = 'front.login'


def create_app(config):
    """
    Args:
        config (str): 应用运行配置
    """
    app = Flask(__name__)
    app.config.from_object(configs.get(config))

    register_blueprints(app)
    register_extensions(app)
    register_filters(app)
    db.init_app(app)
    Migrate(app, db)
    configure_uploads(app, photos)
    return app

