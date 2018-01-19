#!/usr/bin/env python3
# encoding: utf-8


from flask import Flask
from flask_migrate import Migrate

from jobplus.config import configs
from jobplus.models import db


def register_blueprints(app):
    from .handlers import front, company, job, seeker, admin

    app.register_blueprint(front)
    app.register_blueprint(company)
    app.register_blueprint(job)
    app.register_blueprint(seeker)
    app.register_blueprint(admin)


def create_app(config):
    """
    Args:
        config (str): 应用运行配置
    """
    app = Flask(__name__)
    app.config.from_object(configs.get(config))
    db.init_app(app)
    Migrate(app, db)
    register_blueprints(app)
    return app

