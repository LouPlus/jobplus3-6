#!/usr/bin/env python3
# encoding: utf-8


from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_uploads import configure_uploads, patch_request_class

from jobplus.config import configs
from jobplus.models import db, User
from jobplus.forms import photos

import datetime


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

