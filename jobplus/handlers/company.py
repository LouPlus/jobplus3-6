#!/usr/bin/env python3
# encoding: utf-8


from flask import Blueprint, render_template, flash, redirect, \
                  url_for, current_app, request
from flask_login import login_user, current_user, login_required

from jobplus.models import User, Company, db
from jobplus.forms import CompanyRegisterForm, CompanyProfileForm
from jobplus.decorators import company_required
from .job import job


company = Blueprint('company', __name__, url_prefix='/company')


@company.route('/register', methods=['GET', 'POST'])
def register():
    user = User()
    form = CompanyRegisterForm()
    role = user.ROLE_COMPANY
    if not current_user.is_authenticated:
        if form.validate_on_submit():
            form.create_company(role)
            user = user.query.filter_by(username=form.username.data).first()
            login_user(user, True)
            return redirect(url_for('company.company_profile'))
        return render_template('company/register.html', form=form)
    else:
        return redirect(url_for('company.company_profile'))


@company.route('/profile', methods=['GET', 'POST'])
@company_required
def company_profile():
    form = CompanyProfileForm()
    del form.name
    if form.validate_on_submit():
        form.add_company_profile(current_user.id, current_user.username)
        flash('企业用户注册成功！','success')
        return redirect(url_for('front.index'))
    return render_template('company/profile.html', form=form)


@company.route('/')
def company_list():
    page = request.args.get('page', default=1, type=int)
    pagination = Company.query.paginate(
        page=page,
        per_page=current_app.config['LIST_PER_PAGE'],
        error_out=False
    )
    return render_template('company/list.html', pagination=pagination)


@company.route('/<int:company_id>')
def company_detail(company_id):
    company = Company.query.get_or_404(company_id)
    if company.view_count is None:
        company.view_count = 0
    company.view_count += 1
    db.session.add(company)
    db.session.commit()
    return render_template('company/detail.html', company_obj=company)

@company.route('/follow/<int:company_id>')
@login_required
def follow(company_id):
    company = Company.query.get_or_404(company_id)
    if current_user in company.follows:
        company.follows.remove(current_user)
    else:
        company.follows.append(current_user)
    db.session.add(company)
    db.session.commit()
    return redirect(url_for('company.company_detail', company_id=company_id))


@company.route('/job/admin')
@company_required
def job_admin():
    page = request.args.get('page', default=1, type=int)
    id = request.args.get('id', default=1, type=int)
    filters = {
        Job.company_id == current_user.company_info.id,
        Job.status != Job.STATUS_DELETE
    }
    pagination = Job.query.filter(*filters).order_by(Job.updated_at.desc()).paginate(
        page=page,
        per_page=current_app.config['LIST_PER_PAGE'],
        error_out=False
    )
    return render_template('company/admin/jobs.html', pagination=pagination)


@company.route('/job/status/<int:job_id>')
@company_required
def job_status(job_id):
    job = Job.query.get_or_404(job_id)
    online = Job.STATUS_OPENED
    offline = Job.STATUS_CLOSED
    if job.status == online:
        job.status = offline
    elif job.status == offline:
        job.status = online
    db.session.add(job)
    db.session.commit()
    return redirect(url_for('company.job_admin'))


@company.route('/job/delete/<int:job_id>')
@company_required
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    job.status = Job.STATUS_DELETE
    db.session.add(job)
    db.session.commit()
    return redirect(url_for('company.job_admin'))