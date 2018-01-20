#!/usr/bin/env python3
# encoding: utf-8

from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SelectField, IntegerField, SubmitField, PasswordField, ValidationError
from wtforms.validators import Length, Email, EqualTo, Required
from jobplus.models import db, Seeker, User


class UserinfoForm(FlaskForm):
    username = StringField('用户名', validators=[Required(), Length(3, 24)])
    gender = RadioField('性别', choices=[('10', '男'), ('20', '女')])
    phone = StringField('电话', validators=[Required(), Length(8, 24)])
    name = StringField('真实姓名', validators=[Required(), Length(3, 24)])
    college = StringField('毕业院校', validators=[Required(), Length(3, 24)])
    education = SelectField('学历', choices=[
        ('10', '大专'),
        ('20', '本科'),
        ('40', '研究生'),
        ('30', '博士'),
        ('50', '其他')
    ])
    major = StringField('专业',validators=[Required(), Length(3, 24)])
    service_year = IntegerField('工作年限',validators=[Required()])
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
    username = StringField('用户名', validators=[Required(), Length(3, 24)])
    email = StringField('邮箱', validators=[Required(), Email()])
    password = PasswordField('密码', validators=[Required(), Length(6, 24)])
    repeat_password = PasswordField('重复密码', validators=[Required(), EqualTo('password')])
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
