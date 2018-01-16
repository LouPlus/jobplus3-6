#!/usr/bin/env python3
# encoding: utf-8


from flask import Blueprint


job = Blueprint('job', __name__, url_prefix='/jobs')

