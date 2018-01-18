#!/usr/bin/env python3

"""
@version: ??
@author: Lvix
@project: jobplus3-6
@file: generate_db_test_data.py
@time: 18/1/18 6:19
"""

from jobplus.models import *
from faker import Faker
from random import randint

fake = Faker()
fake_cn = Faker('zh_CN')


def gen_phone_num():
    """
    生成11位电话号码
    :return:
    """
    return '1{:0>5d}'.format(randint(0, 99999)) + '{:0>5d}'.format(randint(0, 99999))


def gen_occupation():
    """
    生成职位
    :return:无
    """
    occ_levels = ['初级', '中级', '高级', '超级']
    occ_titles = ['工程师', '产品经理', '产品总监', '运营', '销售', '设计师', '文案', '会计', '法务']
    return occ_levels[randint(0, len(occ_levels) - 1)] + fake_cn.word() + occ_titles[randint(0, len(occ_levels) - 1)]


def iter_users(num, role):
    """
    生成用户
    :param num: 生成数量
    :param role:指定用户角色 User.ROLE_xx
    :return: 无
    """
    for i in range(num):
        while True:
            email = fake_cn.email()
            username = email.split('@')[0]
            if User.query.filter_by(email=email).first() is None or \
                    User.query.filter_by(username=username).first() is None:
                break

        # print('Creating user: {}'.format(username))
        yield User(
            username=username,
            email=email,
            password='123456',
            role=role
        )


def iter_seekers(seekers):
    """
    生成求职者信息
    :param seekers: 求职者列表
    :return:
    """
    gender_list = [10, 20]
    edu_list = [10, 20, 30, 40, 50]
    for seeker in seekers:
        name = fake_cn.name()
        # print('Creating seeker: {}'.format(name))
        yield Seeker(
            user=seeker,
            gender=gender_list[randint(0, 1)],
            phone=gen_phone_num(),
            name=name,
            college=fake_cn.word() + '大学',
            education=edu_list[randint(0, 4)],
            major=fake_cn.word() + '工程',
            service_year=randint(0, 11)
        )


def iter_companies(companies):
    """
    生成公司信息
    :param companies: 公司列表
    :return:
    """
    for company in companies:

        while True:
            name = fake_cn.word() + '股份有限公司'
            if Company.query.filter_by(name=name).first() is None:
                break

        # print('Creating company: {}'.format(name))
        yield Company(
            user=company,
            name=name,
            city=fake_cn.city(),
            address=fake_cn.address(),
            email=fake_cn.email(),
            phone=gen_phone_num(),
            fax=gen_phone_num(),
            manager_name=fake_cn.name(),
            manager_job='CEO',
        )


def iter_jobs(companies):
    """
    为每家公司生成一个职位
    :param companies: 包含User实例的列表
    :return:
    """
    for company in companies:
        if company.role == User.ROLE_COMPANY:
            if randint(0, 1):
                sal_min = randint(50, 200) * 100
                sal_max = sal_min + randint(10, 200) * 10
            else:
                sal_min = 0
                sal_max = 0
            yield Job(
                user=company,
                title=gen_occupation(),
                salary_min=sal_min,
                salary_max=sal_max,
                exp_required=randint(1, 6),
                edu_required=randint(1, 5) * 10,
                description=fake_cn.text()[:140],
                work_address=company.company_info.address
            )


def iter_resumes(seekers):
    """
    为每个求职者生成一份简历
    :param seekers: 包含User实例的列表
    :return: 无
    """
    for seeker in seekers:
        if seeker.role == User.ROLE_SEEKER:
            sal_min = randint(50, 200) * 100
            sal_max = sal_min + randint(10, 200) * 10
            edu_exp_start = 1990 + randint(10, 20)
            edu_exp_time = str(edu_exp_start) + '~' + str(edu_exp_start + 4)
            yield Resume(
                user=seeker,
                resume_type=Resume.TYPE_WEB_RESUME,
                expect_salary_min=sal_min,
                expect_salary_max=sal_max,
                edu_exp=edu_exp_time + ' 于 ' + seeker.seeker_info.college + '就读',
                project_exp='我的项目经验有：\n' + fake_cn.sentence() + '\n' + fake_cn.sentence(),
                expect_job='我希望获得一份' + gen_occupation() + '的工作'
            )


def simulate_delivery(resumes, jobs):
    """
    模拟简历投递
    :param resumes: 简历列表
    :param jobs: 职位列表
    :return: 无
    """
    for resume in resumes:
        # 模拟每份简历投递0~3次
        for i in range(randint(0, 3)):
            # 随机选取一份简历
            job = jobs[randint(0, len(jobs) - 1)]
            if job not in resume.jobs:
                resume.jobs.append(job)
        db.session.add(resume)
    db.session.commit()


def simulate_following(seekers, jobs):
    """
    模拟用户关注职位
    :param seekers: 求职者列表
    :param jobs: 职位列表
    :return: 无
    """
    for seeker in seekers:
        if seeker.role == User.ROLE_SEEKER:
            for i in range(randint(0, 3)):
                job = jobs[randint(0, len(jobs) - 1)]
                if job not in seeker.following_jobs:
                    seeker.following_jobs.append(job)
            db.session.add(seeker)
    db.session.commit()


def empty_table(table):
    print('清空 {} '.format(table.__tablename__))
    items = table.query.all()
    for item in items:
        db.session.delete(item)
    db.session.commit()


def empty_db():
    """
    执行run() 前可以选择性执行本函数，
    将清空以下几个表
    :return:
    """
    try:
        print('---开始清空数据表---')
        empty_table(User)
        empty_table(Seeker)
        empty_table(Company)
        empty_table(Resume)
        empty_table(Job)
        print('---清空完毕---')
    except Exception as e:
        print(e)
        db.session.rollback()


def run(user_num=20, company_num=20, clearing_db=False):
    """
    生成测试数据，默认生成20个求职者，20个公司，
    并为每个求职者生成一份简历，
    每份简历会被投递到0~3个职位
    每位用户会随机关注0~3个职位
    :param user_num: 生成的用户数量
    :param company_num: 生成的公司数量
    :param clearing_db: 生成数据之前是否清理数据库，默认False
    :return:
    """
    try:
        if clearing_db:
            empty_db()
        print('---测试开始---')
        print('开始生成用户')
        test_seekers = list(iter_users(user_num, User.ROLE_SEEKER))
        for seeker in test_seekers:
            db.session.add(seeker)
        db.session.commit()

        print('开始生成公司')
        test_companies = list(iter_users(company_num, User.ROLE_COMPANY))
        for company in test_companies:
            db.session.add(company)
        db.session.commit()

        print('开始生成求职者信息')
        test_seekers_info = list(iter_seekers(test_seekers))
        for seeker_info in test_seekers_info:
            db.session.add(seeker_info)
        db.session.commit()

        print('开始生成公司信息')
        test_companies_info = list(iter_companies(test_companies))
        for company_info in test_companies_info:
            db.session.add(company_info)
        db.session.commit()

        print('开始生成简历和职位')
        test_resumes = list(iter_resumes(test_seekers))
        test_jobs = list(iter_jobs(test_companies))
        for resume in test_resumes:
            db.session.add(resume)
        for job in test_jobs:
            db.session.add(job)
        db.session.commit()

        print('正在进行模拟投递')
        simulate_delivery(test_resumes, test_jobs)

        print('正在进行模拟关注')
        simulate_following(test_seekers, test_jobs)
        print('---数据生成完毕！---')
    except Exception as e:
        print(e)
        db.session.rollback()
