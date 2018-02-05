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
        return re.split(r",|\.|;|，|；|、|/|\\", sentence)

    @app.template_filter()
    def ex_link(url):
        url = str(url)
        if 'http://' in url or 'https://' in url:
            return url
        else:
            return "http://" + str(url)

    @app.template_filter()
    def long_string_cutter(long_string, max_length=20):
        """
        把长字符串按字符数剪短
        :param long_string: 待处理的字符串
        :param max_length: 最大长度
        :return: 处理后的字符串

        示例：
        example_str = '一二三四五六七八九十一二三四五六'
        {{ example_str  | long_string_cutter(12)}}
        返回值为
        '一二三四五六七八九十……'
        """
        if len(long_string) > max_length:
            return long_string[:max_length-2] + '……'
        else:
            return long_string

    @app.template_filter()
    def utc_to_cst(date_time):
        timenow = (date_time + datetime.timedelta(hours=8))
        return timenow


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
    login_manager.login_message = '请登录后操作！'
    login_manager.login_message_category = "danger"


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

