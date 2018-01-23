#!/usr/bin/env python3
# encoding: utf-8

from functools import wraps

from flask import abort
from flask_login import current_user

from jobplus.models import User


def role_required(role_type):
    """ 对用户角色进行判断，保护针对特定用户角色访问的路由只能被特定用户访问，否则引发404错误。

        @role_required(User.ROLE_COMPANY)
        def company():
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role_type:
                abort(404)
            return func(*args, **kwargs)
        return wrapper
    return decorator


seeker_required = role_required(User.ROLE_SEEKER)
company_required = role_required(User.ROLE_COMPANY)
admin_required = role_required(User.ROLE_ADMIN)
