#!/usr/bin/env python3

"""
@version: 0.0.1
@author: Lvix
@project: jobplus3-6
@file: admin_forms.py
@time: 18/1/23 19:10
"""

import datetime
import os

from PIL import Image

from flask import current_app
from flask_wtf import FlaskForm
from flask_uploads import UploadSet, IMAGES
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, ValidationError, SelectField, TextAreaField, DateField, SubmitField
from wtforms.validators import Length, Email, EqualTo, DataRequired, URL

from jobplus.models import db, User, Seeker, Company
from jobplus.forms import CompanyRegisterForm, CompanyProfileForm

from werkzeug.utils import secure_filename


class SeekerBaseForm(FlaskForm):
    """
    求职者信息编辑表单
    """

    email = StringField('邮箱', validators=[DataRequired(message='邮箱地址不可为空'), Email(message='请正确填写邮箱地址')])
    # 修改信息时密码可以为空

    name = StringField('真实姓名', validators=[DataRequired(message='请输入真实姓名'), Length(2, 24)])
    gender = SelectField('性别', choices=[(10, '男'), (20, '女')], coerce=int)
    phone = StringField('电话', validators=[DataRequired(message='请输入电话号码'), Length(11, 11, message='电话号码长度应为11位')])
    college = StringField('毕业院校', validators=[DataRequired(message='该字段不可为空'), Length(2, 24, message='请正确填写院校信息')])
    education = SelectField('学历', choices=[
        (1, '专科'),
        (2, '本科'),
        (4, '硕士'),
        (3, '博士'),
        (5, '其他')
    ], coerce=int)
    major = StringField('专业', validators=[DataRequired(message='该字段不可为空'), Length(3, 24, message='请正确填写专业信息')])
    service_year = SelectField('工作年限', choices=[
        (0, '毕业应届生'),
        (1, '1年'),
        (2, '2年'),
        (3, '3年'),
        (4, '4年'),
        (5, '5年'),
        (6, '6年'),
        (7, '7年'),
        (8, '8年'),
        (9, '9年'),
        (10, '10年'),
        (11, '10年以上')
    ], coerce=int)

    def update_user_info(self):
        """
        更新用户信息
        :return: user模型实例
        """
        user = self.user
        user.email = self.email.data
        user.role = User.ROLE_SEEKER
        if self.is_new_user:
            user.password = self.password.data
            user.username = self.username.data
        else:
            if self.password.data:
                user.password = self.password.data
        db.session.add(user)
        db.session.commit()

        seeker = Seeker(user=user)
        seeker.gender = self.gender.data
        seeker.phone = self.phone.data
        seeker.name = self.name.data
        seeker.college = self.college.data
        seeker.education = self.education.data
        seeker.major = self.major.data
        seeker.service_year = self.service_year.data
        db.session.add(seeker)
        db.session.commit()
        return user


class SeekerEditForm(SeekerBaseForm):
    is_new_user = False
    # 新密码，可以为空
    password = PasswordField('新密码')
    repeat_password = PasswordField('重复密码', validators=[EqualTo('password', message='两次输入的密码不一致')])
    submit = SubmitField('更新信息')

    def __init__(self, user):
        """
        初始化
        """
        super(SeekerEditForm, self).__init__()
        self._fields.move_to_end(self.submit.name, last=True)
        self.user = user

    def validate_email(self, field):
        # 尝试按新 email 去查询
        q_user = User.query.filter_by(email=field.data).first()
        if q_user:
            if self.user.id != q_user.id:
                raise ValidationError('邮箱已经存在')

    def validate_password(self, field):
        # 修改用户信息
        if len(field.data) != 0 and not 6 <= len(field.data) <= 24:
            raise ValidationError('密码长度应为6~24个字符')

    def load_user_info(self):
        """
        从数据库加载用户信息
        :return: user模型实例
        """
        user = self.user
        seeker = user.seeker_info
        if user and seeker:
            self.email.data = user.email
            self.phone.data = seeker.phone
            self.name.data = seeker.name
            self.gender.data = seeker.gender
            self.phone.data = seeker.phone
            self.college.data = seeker.college
            self.education.data = seeker.education
            self.major.data = seeker.major
            self.service_year.data = seeker.service_year
        return user


class SeekerCreateForm(SeekerBaseForm):
    is_new_user = True
    user = User()

    password = PasswordField('密码', validators=[DataRequired(message='密码不可为空'),
                                               Length(6, 24, message='密码长度应为6~24个字符')])
    repeat_password = PasswordField('重复密码', validators=[DataRequired(message='密码不可为空'),
                                                        EqualTo('password', message='两次输入的密码不一致')])
    username = StringField('用户名', validators=[DataRequired(message='用户名不可为空'), Length(3, 24)])
    submit = SubmitField('创建用户')

    def __init__(self):
        """
        初始化，主要为了把重写的 Fields 移到前面
        """
        super(SeekerCreateForm, self).__init__()
        self._fields.move_to_end(self.repeat_password.name, last=False)
        self._fields.move_to_end(self.password.name, last=False)
        self._fields.move_to_end(self.username.name, last=False)
        self._fields.move_to_end(self.submit.name, last=True)

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已经存在')

    def validate_username(self, field):
        user = User.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError('用户名已存在')


# 企业部分
photos = UploadSet('photos', IMAGES)


class CompanyBaseForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired('请输入邮箱'), Email(message='请输入合法的Email地址')])
    # 详情
    name = StringField('公司名称', validators=[DataRequired(message='请输入公司名称'), Length(2, 128)],
                       render_kw={"placeholder": "请输入公司名称"})
    web_url = StringField('公司网址', validators=[DataRequired(message='请输入公司网址'), Length(5, 256), URL],
                          render_kw={"placeholder": "请输入公司网站地址"})
    manager_name = StringField('招聘负责人', validators=[DataRequired(message='请输入招聘负责人姓名')],
                               render_kw={"placeholder": "请输入招聘负责人"})
    manager_job = StringField('负责人职位', validators=[DataRequired(message='请输入招聘负责人职位')],
                              render_kw={"placeholder": "请输入招聘负责人职位"})
    # manager_img = FileField('招聘负责人头像', validators=[FileAllowed(photos, '只能上传图片')])
    resume_email = StringField('接收简历邮箱', validators=[DataRequired(message='请输入接收简历的公司邮箱'), Email()])
    phone = StringField('联系电话', render_kw={"placeholder": "请输入公司联系电话"})
    fax = StringField('传真', render_kw={"placeholder": "请输入公司传真"})
    found_date = DateField('公司创建时间', validators=[DataRequired(message='请选择公司注册时间')], default=datetime.datetime.now())
    city = StringField('公司所在城市', validators=[DataRequired(message='请输入公司所在城市')],
                       render_kw={"placeholder": "请输入公司所在城市"})
    address = StringField('公司地址', validators=[Length(8, 128, message='地址字数限制在8-128位')],
                          render_kw={"placeholder": "请输入公司地址"})
    scale = SelectField('公司人数', choices=[
        ('0', '少于15人'),
        ('1', '15-50人'),
        ('2', '50-150人'),
        ('3', '150-500人'),
        ('4', '大于500人')])
    industry = StringField('所在行业', render_kw={"placeholder": "通信 互联网 硬件..."})
    slogan = StringField('Slogan', render_kw={"placeholder": "请输入公司Slogan"})
    products_display = TextAreaField('公司产品简介', render_kw={"placeholder": "请输入公司产品名称"})
    description = TextAreaField('公司描述', render_kw={"placeholder": "请输入公司描述信息"})

    def change_img(self, field_data, user_id):
        """将用户上传的图片压缩为 100*100 比例进行存储
        Args：
            field_data (filed.data): 图片表单数据
            user_id (int) : 用户ID
        """
        if field_data is None:
            filename = 'avatar_default.jpg'
            return filename
        import os
        filename = str(user_id) + '_' + secure_filename(field_data.filename)
        size = (100, 100)
        img_path = current_app.config['UPLOADED_PHOTOS_DEST']

        im = Image.open(field_data)
        im.thumbnail(size)
        im.save(os.path.join(img_path, filename))
        return filename

    def update_user_info(self):
        """
        更新企业用户信息
        :return: User 模型实例
        """
        user = self.user
        user.email = self.email.data
        user.role = User.ROLE_COMPANY
        if self.is_new_user:
            user.password = self.password.data
            user.username = self.username.data
        else:
            if self.password.data:
                user.password = self.password.data
        db.session.add(user)
        db.session.commit()

        if self.is_new_user:
            company = Company(user=user)
        else:
            company = user.company_info

        # logo = self.logo.data
        # manager_img = self.manager_img.data
        # if logo:
        #     company.logo = self.change_img(logo, user.id)
        # if manager_img:
        #     company.manager_photo = self.change_img(manager_img, user.id)

        company.name = self.name.data
        company.web_url = self.web_url.data
        company.found_date = self.found_date.data
        company.city = self.city.data
        company.address = self.address.data
        company.scale = self.scale.data
        company.industry = self.industry.data
        company.email = self.resume_email.data
        company.phone = self.phone.data
        company.fax = self.fax.data
        company.manager_name = self.manager_name.data
        company.manager_job = self.manager_job.data

        company.slogan = self.slogan.data
        company.products_display = self.products_display.data
        company.description = self.description.data
        db.session.add(company)
        db.session.commit()
        return user


class CompanyEditForm(CompanyBaseForm):
    username = None
    is_new_user = False

    logo_url = None
    manager_img_url = None

    password = PasswordField('新密码')
    repeat_password = PasswordField('重复密码', validators=[EqualTo('password', message='两次输入的密码不一致')])
    submit = SubmitField('更新信息')
    # logo = FileField('公司LOGO', validators=[FileAllowed(photos, '只能上传图片文件！'), FileRequired('文件未选择！')])

    def __init__(self, user):
        super(CompanyEditForm, self).__init__()
        self.user = user
        # self._fields.move_to_end(self.logo.name, last=False)
        self._fields.move_to_end(self.email.name, last=False)
        self._fields.move_to_end(self.submit.name, last=True)

    def load_user_info(self):
        """
        从数据库加载信息
        :return:
        """
        user = self.user
        company = user.company_info

        self.email.data = user.email

        self.logo_url = company.logo
        self.manager_img_url = company.manager_photo

        self.name.data = company.name
        self.web_url.data = company.web_url
        self.found_date.data = company.found_date
        self.city.data = company.city
        self.address.data = company.address
        self.scale.data = company.scale
        self.industry.data = company.industry
        self.resume_email.data = company.email
        self.phone.data = company.phone
        self.fax.data = company.fax
        self.manager_name.data = company.manager_name
        self.manager_job.data = company.manager_job

        return user

    def validate_email(self, field):
        # 尝试按新 email 去查询
        q_user = User.query.filter_by(email=field.data).first()
        if q_user:
            if self.user.id != q_user.id:
                raise ValidationError('邮箱已经存在')

    def validate_password(self, field):
        # 修改用户信息
        if len(field.data) != 0 and not 6 <= len(field.data) <= 24:
            raise ValidationError('密码长度应为6~24个字符')

    def validate_name(self, field):
        q_user = Company.query.filter_by(name=field.data).first()
        if q_user:
            if self.user.company_info.id != q_user.id:
                raise ValidationError('该公司已注册')


class CompanyCreateForm(CompanyBaseForm):
    is_new_user = True
    user = User()

    username = StringField('用户名', validators=[DataRequired(message='用户名不可为空'), Length(3, 24)])
    password = PasswordField('密码', validators=[DataRequired(message='密码不可为空'), Length(6, 24, message='密码长度应为6~24个字符')])
    repeat_password = PasswordField('重复密码', validators=[DataRequired(message='密码不可为空'), EqualTo('password', message='两次输入的密码不一致')])
    submit = SubmitField('创建用户')

    def __init__(self):
        """
        初始化，主要为了把重写的 Fields 移到前面
        """
        super(CompanyCreateForm, self).__init__()
        self._fields.move_to_end(self.repeat_password.name, last=False)
        self._fields.move_to_end(self.password.name, last=False)
        self._fields.move_to_end(self.email.name, last=False)
        self._fields.move_to_end(self.username.name, last=False)
        self._fields.move_to_end(self.submit.name, last=True)

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已经存在')

    def validate_username(self, field):
        user = User.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError('用户名已存在')

    def validate_name(self, field):
        company = Company.query.filter_by(name=field.data).first()
        if company:
            raise ValidationError('该公司已注册')