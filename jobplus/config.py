#!/usr/bin/env python3
# encoding: utf-8

import os


class BaseConfig(object):
    SECRET_KEY = 'makesure to set a very secret key'
    INDEX_PER_PAGE = 12
    LIST_PER_PAGE = 15


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root:12345678@localhost:3306/jobplus3?charset=utf8'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_AUTO_RELOAD = True
    # 企业相关图片文件路径
    UPLOADED_PHOTOS_DEST = os.getcwd() + '/jobplus/static/company_img'


class ProductionConfig(BaseConfig):
    DEBUG = False


class TestingConfig(BaseConfig):
    pass


configs = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}
