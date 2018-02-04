#!/usr/bin/env python3
# encoding: utf-8


from flask import Blueprint, render_template
from flask import request, current_app, flash, redirect, url_for, abort
from jobplus.models import Job, db, User
from jobplus.decorators import roles_required

job = Blueprint('job', __name__, url_prefix='/job')


@job.route('/')
def list():
    page = request.args.get('page', default=1, type=int)
    pagination = Job.query.paginate(
        page=page,
        per_page=current_app.config['INDEX_PER_PAGE'],
        error_out=False
    )
    # lists = Job.query.all()
    # newest_jobs = Job.query.order_by(db.desc(Job.created_at)).limit(9).all()
    return render_template('job/list.html', pagination=pagination)


@job.route('/<int:job_id>')
def detail(job_id):
    return render_template('job/detail.html', job=Job.query.get_or_404(job_id))


@job.route('/<int:job_id>/enable')
@roles_required(User.ROLE_COMPANY, User.ROLE_ADMIN)
def enable(job_id):
    """
    职位状态切换视图，页面渲染时建议使用 next=url_for('some_view') 指定执行后的页面
    :param job_id: 职位id
    :return:
    """
    tar_job = Job.query.filter_by(id=job_id).first()
    if tar_job:
        if tar_job.status == Job.STATUS_CLOSED:
            tar_job.status = Job.STATUS_OPENED
            db.session.add(tar_job)
            db.session.commit()
            flash('职位{} 开始招聘'.format(tar_job.title), 'success')
    else:
        abort(404)
    return redirect(request.args.get('next') or url_for('job.detail', job_id=job_id) or url_for('front.index'))


@job.route('/<int:job_id>/disable')
@roles_required(User.ROLE_COMPANY, User.ROLE_ADMIN)
def disable(job_id):
    """
    职位状态切换视图，页面渲染时建议使用 next=url_for('some_view') 指定执行后的页面
    :param job_id: 职位id
    :return:
    """
    tar_job = Job.query.filter_by(id=job_id).first()
    if tar_job:
        if tar_job.status == Job.STATUS_OPENED:
            tar_job.status = Job.STATUS_CLOSED
            db.session.add(tar_job)
            db.session.commit()
            flash('职位{} 结束招聘'.format(tar_job.title), 'warning')
    else:
        abort(404)
    return redirect(request.args.get('next') or url_for('job.detail', job_id=job_id) or url_for('front.index'))