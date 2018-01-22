#!/usr/bin/env python3
# encoding: utf-8

import os
from flask import Blueprint, render_template, flash, redirect, url_for, request, current_app
from flask_uploads import UploadSet, IMAGES
from flask_login import login_user, current_user
from werkzeug.datastructures import CombinedMultiDict
from werkzeug.utils import secure_filename
from jobplus.models import User
from jobplus.forms import CompanyRegisterForm, CompanyProfileForm, photos
from jobplus.decorators import company_required


company = Blueprint('company', __name__, url_prefix='/company')



@company.route('/register', methods=['GET', 'POST'])
def register():
    user = User()
    form = CompanyRegisterForm()
    role = user.ROLE_COMPANY
    if not current_user.is_authenticated:
        if form.validate_on_submit():
            form.create_company(role)
            flash('注册成功！', 'success')
            user = user.query.filter_by(username=form.username.data).first()
            login_user(user, True)
            return redirect(url_for('company.company_profile'))
        return render_template('company/register.html', form=form)
    else:
        return redirect(url_for('company.company_profile'))


@company.route('/profile', methods=['GET', 'POST'])
@company_required
def company_profile():
    values = CombinedMultiDict([request.files,request.form])
    form = CompanyProfileForm(values)
    if form.validate_on_submit():
        print('hello')
        logo = form.logo.data
        logoname = secure_filename(logo.filename)
        print(logoname)
        file_path = os.path.join('static/company_img',logoname)
        print(file_path)
        print(current_app.config['UPLOADED_PHOTOS_DEST'])
        print(photos.save(logo,))
        print('done')
        # form.add_company_profile(current_user.id)
        return redirect(url_for('front.index'))
    return render_template('company/profile.html', form=form)
