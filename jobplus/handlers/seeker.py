#!/usr/bin/env python3
# encoding: utf-8


from flask import Blueprint, render_template, flash, url_for, redirect
from flask_login import current_user, login_user
from jobplus.forms import UserinfoForm, SeekerRegisterForm
from jobplus.models import Seeker

seeker = Blueprint('seeker', __name__, url_prefix='/user')


@seeker.route('/profile', methods=['GET', 'POST'])
def profile():
    if not current_user.is_seeker:
        return redirect(url_for('front.index'))
    form = UserinfoForm()
    form.load_seeker_info()
    if not Seeker.query.filter_by(user_id=current_user.id).first():
        flash('请完善个人信息', 'success')
    if form.validate_on_submit():
        form.update_user()
        flash('更新成功', 'success')
    return render_template('user.html', form=form)


@seeker.route('/register', methods=['GET', 'POST'])
def register():
    form = SeekerRegisterForm()
    if current_user.is_authenticated:
        # 如果用户已登录，并尝试打开注册页面，会被跳转到profile
        if current_user.is_seeker:
            return redirect(url_for('.profile'))
        else:
            return redirect(url_for('front.index'))
    if form.validate_on_submit():
        user = form.create_user()
        # 注册后登录
        login_user(user, True)
        flash('注册成功，请完善个人信息', 'success')
        return redirect(url_for('.profile'))
    return render_template('seeker_register.html', form=form)

