#!/usr/bin/env python3
# encoding: utf-8

import os
import json
from random import randint, choice

from faker import Faker

from jobplus.models import db, User, Company, Job, Resume, Delivery, Seeker


fake = Faker(locale='zh-cn')
email_set = set()

with open(os.path.join(os.path.dirname(__file__), 'data/company_data.json')) as f:
        company_detail = json.load(f)

def iter_seeker_user():
    for seeker in range(1,10):
        email = fake.email()
        while email in email_set:
            email = fake.email()
        email_set.add(email)
        yield User(
            username = fake.name(),
            email = email,
            password = '123456',
            role = User.ROLE_SEEKER
        )

def iter_resume():
    seekers = User.query.filter_by(role = 20).all()
    for seeker in seekers:
        print(seeker.id)
        yield Resume(
            user_id = seeker.id,
            resume_type = randint(1, 2),
            photo = 'http://img2.woyaogexing.com/2018/01/23/e4ec5a783bc2508a!400x400_big.jpg',
            expect_salary_min = choice([1000,2000,3000,4000,5000]),
            expect_salary_max = choice([6000,7000,8000,9000,10000]),
            edu_exp = fake.text(),
            self_intro = fake.text(),
            project_exp = fake.text(),
            expect_job = fake.sentence(),
        )

def iter_seeker():
    users = User.query.filter_by(role=20).all()
    for user in users:
        yield Seeker(
            user_id = user.id,
            gender = choice([10,20]),
            phone = fake.phone_number(),
            name = fake.name(),
            college = '清华大学',
            education = choice([1,2,3,4,5]),
            major = fake.job(),
            service_year = randint(0,11)
        )

def iter_delivery():
    company = Company.query.filter_by(name='腾讯').first()
    seekers = User.query.filter_by(role=20).limit(5).all()
    for seeker in seekers:
        job = randint(0,19)
        yield Delivery(
            resume_id = seeker.resumes[0].id,
            job_id = company.jobs[job].id,
            company_id = company.id,
            status = 1,
        )

def iter_users():
    for company in company_detail:
        name = company['name']
        email = fake.email()
        while email in email_set:
            email = fake.email()
        email_set.add(email)
        yield User(
            username = name,
            email = email,
            password = '123456',
            role = 30
        )

def get_photo():
    path = os.path.join(os.path.dirname(__file__), 'data/manger_photo.json')
    with open(path) as f:
        manager_img = json.load(f)
    for photo in manager_img:
        yield photo['manager_photo']

def iter_companys():
    photo = get_photo()

    for company in company_detail:
        name = company['name']
        user = User.query.filter_by(username=name).first()
        phone = fake.phone_number()
        yield Company(
            user_id = user.id,
            name = user.username,
            logo = company['image_urls'],
            web_url = company['web_url'],
            found_date = fake.date(),
            city = company['city'],
            address = fake.address(),
            scale = randint(0, 4),
            industry = company['industry'],
            email = fake.email(),
            phone = phone,
            fax = phone,
            manager_name = fake.name(),
            manager_job = fake.job(),
            manager_photo = next(photo),
            slogan = company['slogan'],
            products_display = fake.sentence(),
            description = company['description']
            )

def iter_jobs():
    users = User.query.filter_by(role=30).all()
    job_title = ['运维工程师','Linux系统开发工程师','测试工程师', '金融产品经理','游戏主美', '前端开发工程师',
    '数据开发', '售前工程师', '项目经理', '测试工程师','电商运营', '部门助理', '分公司负责人', '质检专员', '监理',
    '市场推广', '资深视觉设计师', '商务经理', '投资助理', 'web前端']
    for user in users:
        job_quantity = 20
        while job_quantity > 0:
            yield Job(
                title = choice(job_title),
                user_id = user.id,
                salary_min = choice([1000,2000,3000,4000,5000]),
                salary_max = choice([6000,7000,8000,9000,10000]),
                exp_required = randint(0,5),
                edu_required = randint(0,5),
                is_full_time = choice([True, False]),
                description = fake.text(),
                work_address = fake.address(),
                company_id = user.company_info.id
            )
            job_quantity -= 1


def run():
    # for user in iter_users():
    #     db.session.add(user)

    # for company in iter_companys():
    #     db.session.add(company)
    # for job in iter_jobs():
    #     db.session.add(job)

    for user in iter_seeker_user():
        db.session.add(user)
        db.session.commit()

    for resume in iter_resume():
        db.session.add(resume)

    for delivery in iter_delivery():
        db.session.add(delivery)

    for seeker in iter_seeker():
        db.session.add(seeker)
    try:
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()

