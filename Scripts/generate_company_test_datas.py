#!/usr/bin/env python3
# encoding: utf-8

import os
import json
from random import randint

from faker import Faker

from jobplus.models import db, User, Company


fake = Faker(locale='zh-cn')
email_set = set()

with open(os.path.join(os.path.dirname(__file__), 'data/company_data.json')) as f:
        company_detail = json.load(f)

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

def run():
    for user in iter_users():
        db.session.add(user)

    for company in iter_companys():
        db.session.add(company)
    
    try:
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()

