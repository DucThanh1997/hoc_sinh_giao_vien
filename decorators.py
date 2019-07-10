from models.user import UserModel
from functools import wraps
from flask import request, g
from jwt import decode
import re
from messenger import *
from datetime import datetime, timedelta
import datetime
from config import Config


def token_check(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        authorization = request.headers.get("authorization")
        if not authorization:
            return {"error": "mời bạn đăng nhập lại"}, 401
        token = authorization.split(" ")[1]
        yesterday = datetime.datetime.now() - timedelta(days=1)
        today_list = "blacklist_token_in_" + datetime.datetime.now().strftime(
            "%d_%m_%Y"
        )
        yesterday_list = "blacklist_token_in_" + yesterday.strftime("%d_%m_%Y")
        resp = decode(token, None, verify=False, algorithms=["HS256"])
        if (
            Config.REDIS_CONNECTOR.sismember(today_list, resp["jti"]) is True
            or Config.REDIS_CONNECTOR.sismember(yesterday_list, resp["jti"]) is True
        ):
            return {"error": "mời bạn đăng nhập lại"}, 401

        g.id = resp["identity"]
        g.user = UserModel.find_by_user_id(g.id)
        g.jti = resp["jti"]
        return fn(*args, **kwargs)

    return wrapper


def gv_authenticate(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        authorization = request.headers.get("authorization")
        if not authorization:
            return {"error": "Mời bạn đăng nhập lại"}, 401
        token = authorization.split(" ")[1]
        yesterday = datetime.datetime.now() - timedelta(days=1)
        today_list = "blacklist_token_in_" + datetime.datetime.now().strftime(
            "%d_%m_%Y"
        )
        yesterday_list = "blacklist_token_in_" + yesterday.strftime("%d_%m_%Y")
        resp = decode(token, None, verify=False, algorithms=["HS256"])
        if (
            Config.REDIS_CONNECTOR.sismember(today_list, resp["jti"]) is True
            or Config.REDIS_CONNECTOR.sismember(yesterday_list, resp["jti"]) is True
        ):
            return {"error": "mời bạn đăng nhập lại"}, 401

        id = resp["identity"]
        g.user = UserModel.find_by_user_id(id)
        g.jti = resp["jti"]
        if not id or g.user is None:
            return {"error": "không tìm thấy user đăng nhập"}, 404

        if g.user.job != 2:
            return {"error": "không có quyền"}, 401
        return fn(*args, **kwargs)

    return wrapper


def hs_authenticate(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        authorization = request.headers.get("authorization")
        if not authorization:
            return {"error": "không có token"}, 401
        token = authorization.split(" ")[1]
        yesterday = datetime.datetime.now() - timedelta(days=1)
        today_list = "blacklist_token_in_" + datetime.datetime.now().strftime(
            "%d_%m_%Y"
        )
        yesterday_list = "blacklist_token_in_" + yesterday.strftime("%d_%m_%Y")
        resp = decode(token, None, verify=False, algorithms=["HS256"])
        if (
            Config.REDIS_CONNECTOR.sismember(today_list, resp["jti"]) is True
            or Config.REDIS_CONNECTOR.sismember(yesterday_list, resp["jti"]) is True
        ):
            return {"error": "mời bạn đăng nhập lại"}, 401

        id = resp["identity"]
        g.user = UserModel.find_by_user_id(id)
        g.jti = resp["jti"]
        if not id or UserModel.find_by_ma(id) is None:
            return {"error": "không tìm thấy user"}
        if UserModel.UserModel.find_by_user_id(id).chuc_vu != 1:
            return {"error": "không có quyền"}
        return fn(*args, **kwargs)

    return wrapper


def validiate_mail(mail):
    if (
        re.match(
            "^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$",
            mail,
        )
        == None
    ):
        return None
    return 1


def validiate_phone_number(number):
    if re.match("^[0-3]{2}[0-9]{8}$", number) == None:
        return None
    return 1
