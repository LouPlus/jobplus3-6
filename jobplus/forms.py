#!/usr/bin/env python3
# encoding: utf-8

import datetime
import os

from flask import current_app
from flask_wtf import FlaskForm
from flask_uploads import UploadSet, IMAGES
from flask_login import current_user
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename
from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError, TextAreaField, SelectField, DateField
from wtforms.validators import Length, Email, EqualTo, DataRequired, Regexp

from jobplus.models import db, User, Seeker, Company


class LoginForm(FlaskForm):
    # 官方文档建议使用 DataRequired() 代替 Required()
    email = StringField('邮箱', validators=[DataRequired(message='邮箱不可为空'), Email(message='邮箱地址格式不正确')])
    password = PasswordField('密码', validators=[DataRequired(message='密码不可为空'), Length(6, 24, message='密码长度要在6~24个字符之间')])
    remember_me = BooleanField('记住登录')
    submit = SubmitField('登录')

    def validate_email(self, field):
        if not User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱未注册')

    def validate_password(self, field):
        user = User.query.filter_by(email=self.email.data).first()
        if user and not user.check_password(field.data):
            raise ValidationError('密码错误')


class UserinfoForm(FlaskForm):
    # username 不能更改
    # username = StringField('用户名', validators=[DataRequired(), Length(3, 24)])
    name = StringField('真实姓名', validators=[DataRequired(message='请输入您的真实姓名'), Length(2, 24)])
    gender = SelectField('性别', choices=[('10', '男'), ('20', '女')])
    phone = StringField('电话', validators=[DataRequired(message='请输入电话号码'), Length(11, 11, message='电话号码长度应为11位')])
    college = StringField('毕业院校', validators=[DataRequired(message='该字段不可为空'), Length(2, 24, message='请正确填写院校信息')])
    education = SelectField('学历', choices=[
        ('1', '专科'),
        ('2', '本科'),
        ('4', '硕士'),
        ('3', '博士'),
        ('5', '其他')
    ])
    major = StringField('专业', validators=[DataRequired(message='该字段不可为空'), Length(3, 24, message='请正确填写专业信息')])
    service_year = SelectField('工作年限', validators=[DataRequired()],
                               choices=[
                                   ('0', '毕业应届生'),
                                   ('1', '1年'),
                                   ('2', '2年'),
                                   ('3', '3年'),
                                   ('4', '4年'),
                                   ('5', '5年'),
                                   ('6', '6年'),
                                   ('7', '7年'),
                                   ('8', '8年'),
                                   ('9', '9年'),
                                   ('10', '10年'),
                                   ('11', '10年以上')])
    submit = SubmitField('更新信息')

    def update_user(self):

        seeker = Seeker()
        # username 不能更改
        # user.username = self.username.data
        # 连接 user 表
        seeker.user = current_user
        seeker.gender = self.gender.data
        seeker.phone = self.phone.data
        seeker.name = self.name.data
        seeker.college = self.college.data
        seeker.education = self.education.data
        seeker.major = self.major.data
        seeker.service_year = self.service_year.data
        db.session.add(seeker)
        db.session.commit()
        return seeker

    def load_seeker_info(self):
        seeker = Seeker.query.filter_by(user_id=current_user.id).first()
        if seeker:
            self.name.data = seeker.name
            self.gender.data = seeker.gender
            self.phone.data = seeker.phone
            self.college.data = seeker.college
            self.education.data = seeker.education
            self.major.data = seeker.major
            self.service_year.data = seeker.service_year
        return seeker


class SeekerRegisterForm(FlaskForm):
    # TODO 应该由正则表达式 Regexp 来验证用户名，只含数字和字母
    username = StringField('用户名', validators=[DataRequired(message='用户名不可为空'), Length(3, 24)])
    email = StringField('邮箱', validators=[DataRequired(message='邮箱地址不可为空'), Email(message='请正确填写邮箱地址')])
    password = PasswordField('密码', validators=[DataRequired(message='密码不可为空'), Length(6, 24, message='密码长度应为6~24个字符')])
    repeat_password = PasswordField('重复密码', validators=[DataRequired(message='密码不可为空'), EqualTo('password', message='两次输入的密码不一致')])
    submit = SubmitField('注册')

    def create_user(self):
        user = User()
        user.username = self.username.data
        user.email = self.email.data
        user.password = self.password.data
        db.session.add(user)
        db.session.commit()
        return user

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已经存在')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已经存在')


class CompanyRegisterForm(FlaskForm):
    """ 企业注册页面表单模型 """

    username = StringField('用户名', validators=[DataRequired(message='请输入用户名'), Length(4, 24, message='用户名长度请在4-24位'), Regexp('^[a-zA-Z0-9_]{4,24}$',message='请使用数字字符和下划线')])
    email = StringField('邮箱', validators=[DataRequired('请输入邮箱'), Email(message='请输入合法的Email地址')])
    password = PasswordField('密码', validators=[DataRequired('请输入密码'), Length(6, 24)])
    repeat_password = PasswordField('重复密码', validators=[DataRequired('请重复输入密码'), EqualTo('password')])
    submit = SubmitField('提交')

    def validate_username(self, field):
        user_name = User.query.filter_by(username=field.data).first()
        if user_name:
            raise ValidationError('用户名已存在')

    def validate_email(self, field):
        email = User.query.filter_by(email=field.data).first()
        if email:
            raise ValidationError('邮箱已存在')

    def create_company(self, role):
        user = User()
        user.username = self.username.data
        user.email = self.email.data
        user.password = self.password.data
        user.role = role
        db.session.add(user)
        db.session.commit()
        return user


photos = UploadSet('photos', IMAGES)


class CompanyProfileForm(FlaskForm):
    """ 企业详情表单 """

    logo = FileField('企业LOGO', validators=[FileAllowed(photos, '只能上传图片文件！'),FileRequired('文件未选择！')])
    name = StringField('企业名称', validators=[DataRequired(message='请输入企业名称'), Length(4, 128)], render_kw={"placeholder":"请输入企业名称"})
    email = StringField('简历邮箱', validators=[DataRequired(message='请输入接受简历的企业邮箱'), Email()])
    phone = StringField('联系电话', validators=[DataRequired(message='请输入联系电话'), Length(5, 32)])
    fax = StringField('传真')
    found_date = DateField('企业创建时间', validators=[DataRequired(message='请选择企业注册时间')], default=datetime.datetime.now())
    city = StringField('企业所在城市')
    address = StringField('企业地址', validators=[Length(8, 128, message='地址字数限制在8-128位')])
    scale = SelectField('企业人数', choices=[
        ('0', '少于15人'),
        ('1', '15-50人'),
        ('2', '50-150人'),
        ('3', '150-500人'),
        ('4', '大于500人')])
    industry = StringField('所在行业')
    slogan = StringField('一句话简介')
    products_display = TextAreaField('企业产品简介')
    manager_name = StringField('招聘负责人', validators=[DataRequired(message='请输入招聘负责人姓名')])
    manager_job = StringField('负责人职位')
    manager_img = FileField('负责人头像', validators=[FileAllowed(photos, '只能上传图片'), FileRequired('文件未选择！')])
    submit = SubmitField('提交')

    def validate_name(self, field):
        company_name = Company.query.filter_by(name=field.data).first()
        if company_name:
            raise ValidationError('企业已存在')

    def add_company_profile(self, user_id):
        company = Company()

        logo = self.logo.data
        manager_img = self.manager_img.data

        logo_name = secure_filename(logo.filename)
        manager_img_name = secure_filename(manager_img.filename)

        logo_file = photos.save(logo, name=logo_name)
        manager_img_file = photos.save(manager_img, name=manager_img_name)

        img_path = current_app.config['UPLOADED_PHOTOS_DEST']

        company.user_id = user_id
        company.name = self.name.data
        company.logo = os.path.join(img_path, logo_file)
        company.found_date = self.found_date.data
        company.city = self.city.data
        company.address = self.address.data
        company.scale = self.scale.data
        company.industry = self.industry.data
        company.email = self.email.data
        company.phone = self.phone.data
        company.fax = self.fax.data
        company.manager_name = self.manager_name.data
        company.manager_job = self.manager_job.data
        company.manager_photo = os.path.join(img_path, manager_img_file)
        db.session.add(company)
        db.session.commit()
