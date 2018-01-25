#!/usr/bin/env python3
# encoding: utf-8


from flask import Blueprint, render_template, flash, redirect, url_for, current_app, request
from flask_login import login_user, current_user

from jobplus.models import User, Company
from jobplus.forms import CompanyRegisterForm, CompanyProfileForm
from jobplus.decorators import company_required


company = Blueprint('company', __name__, url_prefix='/company')


@company.route('/register', methods=['GET', 'POST'])
def register():
    user = User()
    form = CompanyRegisterForm()
    role = user.ROLE_COMPANY
    if not current_user.is_authenticated:
        if form.validate_on_submit():
            form.create_company(role)
            flash('注册成功！', 'success')
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
    if form.validate_on_submit():
        form.add_company_profile(current_user.id)
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
    return render_template('company/list.html', pagaination=pagination)


@company.route('/<int:company_id>')
def company_detail(company_id):
    company = Company.query.get_or_404(company_id)
    return render_template('company/detail.html', company=company)
