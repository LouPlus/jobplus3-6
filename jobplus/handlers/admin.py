#!/usr/bin/env python3
# encoding: utf-8


from flask import Blueprint, render_template, flash, url_for, request, current_app, redirect

from jobplus.models import db, User, Seeker, Company
from jobplus.admin_forms import SeekerEditForm, SeekerCreateForm, CompanyEditForm, CompanyCreateForm
from flask_login import current_user

admin = Blueprint('admin', __name__, url_prefix='/admin')


# 用户列表
@admin.route('/users', methods=['GET', 'POST'])
def user_list():
    if not current_user.is_admin:
        return redirect(url_for('front.index'))

    page = request.args.get('page', default=1, type=int)
    sw_id = request.args.get('sw_id', default=None, type=int)

    pagination = User.query.paginate(
        page=page,
        per_page=current_app.config['INDEX_PER_PAGE'],
        error_out=False
    )
    if pagination.pages < 7:
        start_page = 1
        end_page = pagination.pages
    else:
        if pagination.page < 3:
            start_page = 1
            end_page = 7
        elif pagination.pages - pagination.page < 3:
            start_page = pagination.pages - 7
            end_page = pagination.pages
        else:
            start_page = pagination.page - 3
            end_page = pagination.page + 3

    if sw_id:
        sw_user = User.query.filter_by(id=sw_id).first()
        if sw_user:
            if not sw_user.status:
                sw_user.status = -1
            else:
                sw_user.status = 0
            db.session.add(sw_user)
            db.session.commit()
        else:
            flash('找不到用户', 'danger')
    return render_template('admin/admin_base.html', pagination=pagination, action='USER_LIST', start_page=start_page, end_page=end_page)


# 添加用户
@admin.route('/users/add', methods=['GET', 'POST'])
def add_user():
    if not current_user.is_admin:
        return redirect(url_for('front.index'))
    action = request.args.get('action')

    if action == 'ADD_SEEKER':
        form = SeekerCreateForm()
    elif action == 'ADD_COMPANY':
        form = CompanyCreateForm()
    else:
        return redirect(url_for('.user_list'))

    if form.validate_on_submit():
        user = form.update_user_info()
        flash('已添加用户 ' + user.username, 'success')
        return redirect(url_for('.user_list'))
    return render_template('admin/admin_edit.html', form=form, action=action)


# 修改用户信息
@admin.route('/users/edit', methods=['GET', 'POST'])
def edit_user():
    if not current_user.is_admin:
        return redirect(url_for('front.index'))
    user_id = request.args.get('user_id', type=int)
    user = User.query.filter_by(id=user_id).first_or_404()
    if user.is_seeker:
        form = SeekerEditForm(user=user)
        action = 'EDIT_SEEKER'
    elif user.is_company:
        form = CompanyEditForm(user=user)
        action = 'EDIT_COMPANY'
    else:
        return redirect(url_for('.user_list'))

    if form.validate_on_submit():
        form.update_user_info()
        flash('已修改用户 #' + str(user.id), 'success')
        print(action)
        return redirect(url_for('admin.edit_user', user_id=user.id, action=action))
    else:
        print(user.id, action)
        form.load_user_info()
    return render_template('admin/admin_edit.html', user_id=user.id, form=form, action=action)
