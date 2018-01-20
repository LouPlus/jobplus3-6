#!/usr/bin/env python3
# encoding: utf-8


from flask import Blueprint, render_template, flash, url_for, redirect
from jobplus.forms import UserinfoForm, SeekerRegisterForm


seeker = Blueprint('seeker', __name__, url_prefix='/user')


@seeker.route('/profile', methods=['GET', 'POST'])
def profile():
    form = UserinfoForm()
    if form.validate_on_submit():
        form.update_user()
        flash('更新成功', 'success')
    return render_template('user.html', form=form)


@seeker.route('/register', methods=['GET', 'POST'])
def register():
    form = SeekerRegisterForm()
    if form.validate_on_submit():
        form.create_user()
        flash('注册成功，请登录！', 'success')
        return redirect(url_for('.profile'))
    return render_template('seeker_register.html', form=form)

