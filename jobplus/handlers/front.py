#!/usr/bin/env python3
# encoding: utf-8


from flask import Blueprint, render_template, url_for, redirect, flash, request, current_app
from jobplus.models import Job, User, Company, db
from jobplus.forms import LoginForm
from flask_login import login_user, logout_user, login_required

front = Blueprint('front', __name__)


@front.route('/')
def index():
    page = request.args.get('page', default=1, type=int)

    # 热门公司列表
    # popular_companies_info = Company.query.order_by(db.desc(Company.total_job_followers)).limit(8).all()

    # 最新公司列表
    newest_companies_info = []
    for company in User.query.filter_by(role=User.ROLE_COMPANY).order_by(db.desc(User.created_at)).limit(8).all():
        newest_companies_info.append(company.company_info)

    # 最新职位列表
    newest_jobs = Job.query.order_by(db.desc(Job.created_at)).limit(9).all()

    # 最热门职位列表
    popular_jobs = Job.query.order_by(db.desc(Job.follower_number)).limit(9).all()

    return render_template('index.html',
                           newest_jobs=newest_jobs,
                           newest_companies_info=newest_companies_info,
                           popular_jobs=popular_jobs)


@front.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        login_user(user, form.remember_me.data)
        flash('欢迎回来，{}'.format(user.username), 'success')
        if user.role == User.ROLE_ADMIN:
            # TODO 应该跳转到管理页面
            return redirect(url_for('.index'))
        elif user.role == User.ROLE_SEEKER:
            # TODO 应该跳转到个人配置页面
            return redirect(url_for('.index'))
        elif user.role == User.ROLE_COMPANY:
            # TODO 应该跳转到企业管理页面
            return redirect(url_for('.index'))
    else:
        for field in form:
            if field.errors:
                flash('登录失败', 'danger')
                break
    return render_template('login.html', form=form)


@front.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已退出登录', 'success')
    return redirect(url_for('.index'))

