#!/usr/bin/env python3
# encoding: utf-8


from flask import Blueprint, render_template
from jobplus.models import Job

job = Blueprint('job', __name__, url_prefix='/jobs')


@job.route('/<int:job_id>')
def detail(job_id):
    # TODO job.html
    return render_template('job.html', job=Job.query.get_or_404(job_id))
