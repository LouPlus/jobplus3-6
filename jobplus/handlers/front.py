#!/usr/bin/env python3
# encoding: utf-8


from flask import Blueprint, render_template
from jobplus.models import Job, Company

front = Blueprint('front', __name__)


@front.route('/')
def index():
    return render_template('index.html')