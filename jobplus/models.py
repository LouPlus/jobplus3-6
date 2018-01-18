#!/usr/bin/env python3
# encoding: utf-8

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()


class Base(db.Model):
    __abstract__ = True
    created_at = db.Column(db.DateTime, default=datetime.utcnow, )
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow())


class User(Base):
    __tablename__ = 'user'

    ROLE_ADMIN = 10
    ROLE_SEEKER = 20
    ROLE_COMPANY = 30

    STATUS_NORMAL = 0
    STATUS_SUSPENDED = -1

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, index=True, nullable=False)
    email = db.Column(db.String(64), unique=True, index=True, nullable=False)
    _password = db.Column('password', db.String(256), nullable=False)
    role = db.Column(db.SmallInteger, default=ROLE_SEEKER)
    status = db.Column(db.SmallInteger, default=STATUS_NORMAL)

    # relationship
    seeker_info = db.relationship('Seeker', uselist=False, backref='user')
    company_info = db.relationship('Company', uselist=False, backref='user')
    jobs = db.relationship('Job', uselist=True, backref='user')
    resumes = db.relationship('Resume', uselist=True, backref='user')

    def __repr__(self):
        return '<User {}: {}>'.format(self.id, self.username)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, orig_password):
        self._password = generate_password_hash(orig_password)

    def check_password(self, password):
        return check_password_hash(self._password, password)

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN

    @property
    def is_seeker(self):
        return self.role == self.ROLE_SEEKER

    @property
    def is_company(self):
        return self.role == self.ROLE_COMPANY


class Seeker(Base):
    __tablename__ = 'seeker'

    # 默认头像的url
    DEFAULT_AVATAR_URL = None
    # 性别
    GENDER_M = 10
    GENDER_F = 20
    # 受教育程度
    EDU_COLLEGE = 10
    EDU_BACHELOR = 20
    EDU_MASTER = 30
    EDU_PHD = 40
    EDU_OTHER = 50

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))

    gender = db.Column(db.SmallInteger, default=GENDER_M, nullable=False)

    phone = db.Column(db.String(11), nullable=False)

    # 真实姓名
    name = db.Column(db.String(32), nullable=False)
    # 头像
    avatar_url = db.Column(db.String(256), default=DEFAULT_AVATAR_URL)
    # 毕业院校
    college = db.Column(db.String(128))
    # 学历
    education = db.Column(db.SmallInteger, default=10, nullable=False)
    # 专业
    major = db.Column(db.String(64))
    # 工作年限：0~11，11表示十年以上
    service_year = db.Column(db.SmallInteger, default=0, nullable=False)

    def __repr__(self):
        return '<Seeker(id={}, name={})>'.format(self.id, self.name)


# 简历表使用 MongoDB, 但暂时写个MySQL原型
class Resume(Base):
    __tablename__ = 'resume'

    TYPE_WEB_RESUME = 1
    TYPE_FILE_RESUME = 2

    # 性别
    GENDER_M = 10
    GENDER_F = 20

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    resume_type = db.Column(db.SmallInteger, default=TYPE_WEB_RESUME, nullable=False)

    photo = db.Column(db.String(256))
    expect_salary_min = db.Column(db.Integer)
    expect_salary_max = db.Column(db.Integer)

    edu_exp = db.Column(db.Text)
    self_intro = db.Column(db.Text)
    project_exp = db.Column(db.Text)
    expect_job = db.Column(db.String(64))
    attachment = db.Column(db.String(256))

    def __repr__(self):
        return '<Resume(id={})>'.format(self.id)


class Company(Base):
    __tablename__ = 'company'

    # 如果不上传Logo
    DEFAULT_LOGO_URL = None

    SCALE_15_LESS = 0
    SCALE_15_50 = 1
    SCALE_50_150 = 2
    SCALE_150_500 = 3
    SCALE_500_MORE = 4

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))

    name = db.Column(db.String(128), unique=True, nullable=False, index=True)
    found_date = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
    city = db.Column(db.String(32), default='北京', nullable=False)
    address = db.Column(db.String(512), nullable=False)
    scale = db.Column(db.SmallInteger, default=SCALE_15_LESS, nullable=False)
    industry = db.Column(db.String(32))
    email = db.Column(db.String(64), nullable=False)
    phone = db.Column(db.String(16), nullable=False)
    fax = db.Column(db.String(16))
    logo = db.Column(db.String(256), default=DEFAULT_LOGO_URL)
    manager_name = db.Column(db.String(32))
    manager_job = db.Column(db.String(32))
    manager_photo = db.Column(db.String(256))

    def __repr__(self):
        return '<Company(id={})>'.format(self.id)


STATUS_SENT = 1
STATUS_CHECKED = 2
STATUS_ACCEPTED = 3
STATUS_REJECTED = 4

Delivery = db.Table('delivery',
                    db.Column('resume_id', db.Integer, db.ForeignKey('resume.id'), primary_key=True),
                    db.Column('job_id', db.Integer, db.ForeignKey('job.id'), primary_key=True),
                    db.Column('status', db.SmallInteger, default=STATUS_SENT, nullable=False)
                    )

# 用户可以关注某个职位
Following = db.Table('following',
                     db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                     db.Column('job_id', db.Integer, db.ForeignKey('job.id'), primary_key=True),
                     db.Column('status', db.SmallInteger, default=STATUS_SENT, nullable=False)
                     )


class Job(Base):
    __tablename__ = 'job'

    # 受教育程度
    EDU_COLLEGE = 10
    EDU_BACHELOR = 20
    EDU_MASTER = 30
    EDU_PHD = 40
    EDU_NO_LIMIT = 50

    # 职位状态，“正在招聘” 和 “招聘结束”
    STATUS_OPENED = 0
    STATUS_CLOSED = -1

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), index=True, nullable=False)
    status = db.Column(db.SmallInteger, default=STATUS_OPENED, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    salary_min = db.Column(db.Integer, default=0)
    salary_max = db.Column(db.Integer, default=0)
    exp_required = db.Column(db.Integer, default=0)
    edu_required = db.Column(db.SmallInteger, default=EDU_NO_LIMIT, nullable=False)
    is_full_time = db.Column(db.Boolean, default=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    work_address = db.Column(db.String(512), nullable=False)

    # relationship
    resumes = db.relationship('Resume', secondary=Delivery, backref=db.backref('jobs'))
    following_users = db.relationship('User', secondary=Following, backref=db.backref('following_jobs'))

    def __repr__(self):
        return '<Job(id={})>'.format(self.id)
