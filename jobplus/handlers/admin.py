#!/usr/bin/env python3
# encoding: utf-8


from flask import Blueprint


admin = Blueprint('admin', __name__, url_prefix='/admin')

