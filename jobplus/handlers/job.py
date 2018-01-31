#!/usr/bin/env python3
# encoding: utf-8


from flask import Blueprint, render_template
from jobplus.models import Job,db
from flask import request,current_app

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
