#!/usr/bin/env python3
# encoding: utf-8


from flask import Blueprint


company = Blueprint('company', __name__, url_prefix='/companies')
