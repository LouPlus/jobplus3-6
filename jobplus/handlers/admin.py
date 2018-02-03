#!/usr/bin/env python3
# encoding: utf-8


from flask import Blueprint, render_template, flash, url_for, request, current_app, redirect
from jobplus.models import db, User, Seeker, Company, Job
from jobplus.admin_forms import SeekerEditForm, SeekerCreateForm, CompanyEditForm, CompanyCreateForm
from jobplus.decorators import roles_required
from flask_login import current_user

admin = Blueprint('admin', __name__, url_prefix='/admin')


# 用户列表
@admin.route('/users', methods=['GET', 'POST'])
@roles_required(User.ROLE_ADMIN)
def user_list():
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
                flash('已禁用用户{}'.format(sw_user.id), 'warning')
            else:
                sw_user.status = 0
                flash('已重新启用用户{}'.format(sw_user.id), 'success')
            db.session.add(sw_user)
            db.session.commit()
        else:
            flash('用户不存在', 'danger')
    return render_template('admin/admin_base.html', pagination=pagination, action='USER_LIST', start_page=start_page, end_page=end_page)


# 添加用户
@admin.route('/users/add', methods=['GET', 'POST'])
@roles_required(User.ROLE_ADMIN)
def add_user():

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
@roles_required(User.ROLE_ADMIN)
def edit_user():

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


@admin.route('/jobs/', methods=['GET', 'POST'])
@roles_required(User.ROLE_ADMIN)
def job_list():

    page = request.args.get('page', default=1, type=int)
    sw_id = request.args.get('sw_id', default=None, type=int)
    sw_status = request.args.get('sw_status', default=None, type=int)

    pagination = Job.query.paginate(
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
        sw_job = Job.query.filter_by(id=sw_id).first()
        if sw_job.status != sw_status and sw_status in [Job.STATUS_CLOSED, Job.STATUS_OPENED]:
            sw_job.status = sw_status
            db.session.add(sw_job)
            db.session.commit()
            if sw_status == Job.STATUS_OPENED:
                flash('职位{} 开始招聘'.format(sw_job.id), 'success')
            elif sw_status == Job.STATUS_CLOSED:
                flash('职位{} 结束招聘'.format(sw_job.id), 'warning')
        else:
            flash('职位不存在', 'danger')
    return render_template('admin/admin_jobs.html', pagination=pagination, action='JOB_LIST', start_page=start_page, end_page=end_page)