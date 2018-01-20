#!/usr/bin/env python3
# encoding: utf-8

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError, TextAreaField, IntegerField, RadioField, SelectField 
from wtforms.validators import Length, Email, EqualTo, DataRequired, URL, NumberRange
from jobplus.models import db, User, Seeker, Company, Resume, Job


class LoginForm(FlaskForm):
    # 官方文档建议使用 DataRequired() 代替 Required()
    email = StringField('邮箱', validators=[DataRequired(message='邮箱不可为空'), Email(message='邮箱地址格式不正确')])
    password = PasswordField('密码', validators=[DataRequired(message='密码不可为空'), Length(6, 24, message='密码长度要在6~24个字符之间')])
    remember_me = BooleanField('记住登录')
    submit = SubmitField('登录')

    def validate_email(self, field):
        if field.data and not User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱未注册')

    def validate_password(self, field):
        user = User.query.filter_by(email=self.email.data).first()
        if user and not user.check_password(field.data):
            raise ValidationError('密码错误')


class UserinfoForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(3, 24)])
    gender = RadioField('性别', choices=[('10', '男'), ('20', '女')])
    phone = StringField('电话', validators=[DataRequired(), Length(8, 24)])
    name = StringField('真实姓名', validators=[DataRequired(), Length(3, 24)])
    college = StringField('毕业院校', validators=[DataRequired(), Length(3, 24)])
    education = SelectField('学历', choices=[
        ('1', '专科'),
        ('2', '本科'),
        ('4', '硕士'),
        ('3', '博士'),
        ('5', '其他')
    ])
    major = StringField('专业',validators=[DataRequired(), Length(3, 24)])
    service_year = IntegerField('工作年限', validators=[DataRequired()])
    submit = SubmitField('更新')

    def update_user(self):
        user = User()
        seeker = Seeker()
        user.username = self.username.data
        seeker.gender = self.gender.data
        seeker.phone = self.phone.data
        seeker.name = self.name.data
        seeker.college = self.college.data
        seeker.education = self.education.data
        seeker.major = self.major.data
        seeker.service_year = self.service_year.data
        return user, seeker


class SeekerRegisterForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(3, 24)])
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[DataRequired(), Length(6, 24)])
    repeat_password = PasswordField('重复密码', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('提交')

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
