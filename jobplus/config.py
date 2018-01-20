#!/usr/bin/env python3
# encoding: utf-8


class BaseConfig(object):
    SECRET_KEY = 'makesure to set a very secret key'
    INDEX_PER_PAGE = 10



class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root@localhost:3306/jobplus?charset=utf8'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_AUTO_RELOAD = True

    
class ProductionConfig(BaseConfig):
    DEBUG = False


class TestingConfig(BaseConfig):
    pass


configs = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}
