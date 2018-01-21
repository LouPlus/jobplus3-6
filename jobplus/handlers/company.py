#!/usr/bin/env python3
# encoding: utf-8


from flask import Blueprint, render_template, flash, redirect, url_for
from flask_uploads import UploadSet, IMAGES

from jobplus.models import User
from jobplus.forms import CompanyRegisterForm, CompanyProfileForm, photos


company = Blueprint('company', __name__, url_prefix='/company')



@company.route('/register', methods=['GET', 'POST'])
def register():
    user = User()
    form = CompanyRegisterForm()
    role = user.ROLE_COMPANY
    if form.validate_on_submit():
        form.create_company(role)
        flash('注册成功！', 'success')
        username = user.query.filter_by(username=form.username.data).first()
        return redirect(url_for('company.company_profile', user_id=username.id))
    return render_template('company/register.html', form=form)


@company.route('/admin/profile?user=<int:user_id>', methods=['GET', 'POST'])
def company_profile(user_id):
    form = CompanyProfileForm()
    if form.validate_on_submit():
        # logoname = photos.save(form.logo.data)
        # photo = companyimg.save(form.manager_photo.data)
        # photo_path = companyimg.path(photo)
        # logo_path = companyimg.path(logo)
        form.add_company_profile(user_id)
        return redirect(url_for('front.index'))
    return render_template('company/profile.html', form=form, user_id=user_id)
