import os
import json
from random import randint

from faker import Faker
from jobplus.models import db, User, Company

fake = Faker(locale='zh-cn')

def iter_users():
    with open(os.path.join(os.path.dirname(__file__),'jobplusspider/jobplusspider/spiders/company_data.json')) as f:
        company_detail = json.load(f)
    for company in company_detail:
        name = company['name']
        yield User(
            username = name,
            email = fake.email(),
            password = '123456',
            role = 30
        )

def iter_company():
    with open(os.path.join(os.path.dirname(__file__),'jobplusspider/jobplusspider/spiders/company_data.json')) as f:
        company_detail = json.load(f)
    with open(os.path.join(os.path.dirname(__file__),'jobplusspider/jobplusspider/spiders/manager_data.json')) as m:
        manager_img = json.load(m)
    for company in company_detail:
        name = company['name']
        user = User.query.filter_by(username=name).first()
        for img in manager_img:
            yield Company(
                name=user.username,
                logo = company['image_urls'],
                web_url = company['web_url'],
                found_date = fake.date(),
                city = company['city'],
                address = fake.address(),
                scale = randint(0, 4),
                industry = company['industry'],
                email = fake.email(),
                phone = fake.phone_number(),
                manager_name = fake.name(),
                manager_job = fake.job(),
                manager_photo = img['manager_photo'],
                slogan = company['slogan'],
                products_display = fake.sentence(),
                description = company['description']
            )