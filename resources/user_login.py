import os
from datetime import datetime
import datetime

from flask_restful import reqparse, Resource
from flask import request, jsonify, send_file
from werkzeug.utils import secure_filename
import werkzeug
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    jwt_required,
    get_jwt_identity,
    get_raw_jwt,
)
import redis

from models.user_login import User_LoginModel
from decorators import *
from messenger import *
from config import Config


class UserReg(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument(
        "user_id",
        type=str,
        required=True,
        help=help.format("user_id")
    )
    parser.add_argument(
        "username", type=str, required=True, help=help.format("username")
    )
    parser.add_argument(
        "password", type=str, required=True, help=help.format("password")
    )

    def post(self):
        data = UserReg.parser.parse_args()
        # check khóa ngoại
        if UserModel.find_by_user_id(user_id=data["user_id"]) is None:
            return {"messages": err_404.format("user")}, 404

        user_login = User_LoginModel(
            # login_id=data["login_id"],
            user_id=data["user_id"],
            username=data["username"],
            password=User_LoginModel.generate_hash(data["password"]),
        )
        try:
            user_login.save_to_db()
        except Exception:
            return {"messages": err_500}, 500

        return {"messages": noti_201}, 201

    @gv_authenticate
    def get(self, user_id=None, page=None, per_page=None):
        if (
            request.args.get("page") and
            request.args.get("per_page") and
            request.args.get("username")
        ):
            page = int(request.args.get("page"))
            username = request.args.get("username")
            per_page = int(request.args.get("per_page"))
            list_user = User_LoginModel.find_list_by_username(
                username, page, per_page
            )
            if list_user is None:
                return {"messages": err_404.format("list_user")}, 404

            return (
                {
                    "list": User_LoginModel.to_json(list_user),
                    "count ": len(list_user)
                },
                200,
            )

        if user_id is None:
            list = User_LoginModel.to_json(
                User_LoginModel.query.paginate(page, per_page, False).items
            )
            return (
                {
                    "list": list,
                    "count": len(User_LoginModel.query.all())
                },
                200
            )

        user_login = User_LoginModel.find_by_user_id(user_id)
        if user_login is None:
            return {"messages": err_404}, 404

        return user_login.json(), 200

    @token_check
    def put(self, ma):
        data = UserReg.parser.parse_args()
        user_login = User_LoginModel.find_by_user_id(ma)
        if user_login is None:
            return {"messages": err_404.format("user_login")}, 404

        if g.user != ma:
            return {"messages": err_404.format("user")}, 404

        try:
            if data["password"]:
                user_login.password = User_LoginModel.generate_hash(
                    data["password"]
                )
            user_login.save_to_db()
        except Exception:
            return {"messages": err_500}, 500

        return {"messages": "update successfully"}, 201

    @gv_authenticate
    def delete(self, user_id):
        user_login = User_LoginModel.find_by_user_id(user_id)
        if user_login is None:
            return {"messages": err_404.format("user_login")}, 404

        try:
            user_login.delete()
        except Exception:
            return {"messages": err_500}, 500

        return {"messages": noti_201}, 200


class UserLogin(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("username", type=str, required=True, help=help)
    parser.add_argument("password", type=str, required=False, help=help)

    def post(self):
        data = UserLogin.parser.parse_args()
        current_user = User_LoginModel.find_by_username(data["username"])
        if not current_user:
            return {"messages": err_404.format("user_login")}, 404

        if UserModel.verify_hash(data["password"], current_user.password):
            access_token = create_access_token(
                identity=User_LoginModel.find_by_username(
                    data["username"]
                ).user_id,
                expires_delta=datetime.timedelta(hours=24),
                fresh=True,
            )
            refresh_token = create_refresh_token(
                identity=User_LoginModel.find_by_username(
                    data["username"]
                ).user_id
            )
            return (
                {
                    "message": "Logged in as {}".format(current_user.username),
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                },
                200,
            )
        else:
            return {"message": Invalid_pass}, 400


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(
            identity=current_user,
            expires_delta=datetime.timedelta(hours=24),
            fresh=False,
        )
        return {"access_token": access_token}, 200


class UserLogout(Resource):
    @token_check
    def post(self):
        time_now = datetime.datetime.now().strftime("%d_%m_%Y")
        language_list = "blacklist_token_in_" + time_now
        print(Config.REDIS_CONNECTOR.exists(language_list))
        if Config.REDIS_CONNECTOR.exists(language_list) == 0:
            try:
                Config.REDIS_CONNECTOR.sadd(language_list, g.jti)
                Config.REDIS_CONNECTOR.expire(language_list, 172800)
            except Exception:
                return {"messages": err_500}, 500

            return {"message": noti_201}, 201
        else:
            try:
                print("113")
                Config.REDIS_CONNECTOR.sadd(language_list, g.jti)
            except Exception:
                return {"messages": err_500}, 500

            return {"message": noti_201}, 201
