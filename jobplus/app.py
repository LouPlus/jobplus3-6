#!/usr/bin/env python3
# encoding: utf-8


from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from jobplus.config import configs
from jobplus.models import db, User


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
    return app

