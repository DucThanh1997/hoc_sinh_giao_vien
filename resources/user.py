import os
from datetime import datetime
import datetime

from flask_restful import reqparse, Resource
from flask import request, jsonify, send_file
from werkzeug.utils import secure_filename

from decorators import *
from config import Config
from messenger import *
from models.user import UserModel


class User(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "user_id",
        type=str,
        required=True,
        help=help.format("user_id")
    )
    parser.add_argument("name", type=str, required=False)
    parser.add_argument("birth_date", type=str, required=False)
    parser.add_argument("phone_number", type=str, required=False)
    parser.add_argument("sex", type=str, required=False)
    parser.add_argument("address", type=str, required=False)
    parser.add_argument("native_land", type=str, required=False)
    parser.add_argument("email", type=str, required=False)
    parser.add_argument("avatar", type=str, required=False)
    parser.add_argument("image_name", type=str, required=False)
    parser.add_argument("job", type=int, required=False)

    def post(self):
        data = User.parser.parse_args()
        if validiate_mail(data["email"]) is None:
            return {"messages": "email wrong form"}, 400

        if validiate_phone_number(data["phone_number"]) is None:
            return {"messages": "phone_number wrong form"}, 400

        user = UserModel(
            user_id=data["user_id"],
            name=data["name"],
            birth_date=datetime.datetime.strptime(
                data["birth_date"], "%Y-%m-%d"
            ),
            phone_number=data["phone_number"],
            sex=data["sex"],
            address=data["address"],
            native_land=data["native_land"],
            email=data["email"],
            job=data["job"],
        )
        try:
            user.save_to_db()
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
            name = request.args.get("username")
            per_page = int(request.args.get("per_page"))
            list_user = UserModel.find_list_by_username(name, page, per_page)
            if list_user is None:
                return {"messages": err_404.format("list_user")}, 404

            return (
                {
                    "list": UserModel.to_json(list_user),
                    "count ": len(list_user)
                },
                200
            )

        if user_id is None:
            list = UserModel.to_json(
                UserModel.query.paginate(page, per_page, False).items
            )
            return {"list": list, "count": len(UserModel.query.all())}, 200

        user = UserModel.find_by_user_id(user_id)
        if user is None:
            return {"messages": err_404.format("user")}, 404
        # nghịch memcache
        return user.json(), 200

    @gv_authenticate
    def put(self, ma):
        data = User.parser.parse_args()
        user = UserModel.find_by_ma(ma)
        if user is None:
            return {"messages": err_404}, 404
        else:
            try:
                if data["user_id"]:
                    user.user_id = data["user_id"]

                if data["name"]:
                    user.name = data["name"]

                if data["birthdate"]:
                    user.birth_date = data["birth_date"]

                if data["sex"]:
                    user.sex = data["sex"]

                if data["native_land"]:
                    user.native_land = data["native_land"]

                if data["email"]:
                    user.email = data["email"]

                if data["job"]:
                    user.job = data["job"]
                user.save_to_db()
            except Exception:
                return {"messages": err_500}, 500

        return {"messages": "update successfully"}, 201

    @gv_authenticate
    def delete(self, user_id):
        user = UserModel.find_by_user_id(user_id)
        if user is None:
            return {"messages": err_404.format("user")}, 404
        try:
            user.delete()
        except Exception:
            return {"messages": err_500}, 500

        return {"messages": noti_201}, 200


class UploadAva(Resource):
    @token_check
    def post(self, ma):
        ten_mien = set(["png", "jpg", "jpeg", "gif"])
        try:
            file_list = request.files.getlist("avatar")
        except Exception:
            return jsonify({"message": "không get được file"})

        for image in file_list:
            image.filename = "{0}.jpg".format(ma)
            filename = image.filename
            if filename.rsplit(".", 1)[1].lower() in ten_mien:
                name_off = secure_filename(filename)
                path = os.path.join(Config.UPLOAD_FOLDER, name_off)
                image.save(path)
                user = UserModel.find_by_ma(ma)
                if user is None:
                    return {"messages": err_404}, 404

                user.image_name = name_off
                user.avatar = path
                try:
                    user.save_to_db()
                except Exception:
                    return {"messages": err_500}, 500

                return {"message": noti_201}, 200
            else:
                return {"message": err_400}, 400

    @token_check
    def get(self, ma):
        """
        kiểm tra user đăng nhập hiện tại có file name giống mình muốn lấy
        không. Làm sau login
        """
        try:
            index_path = os.path.join(Config.UPLOAD_FOLDER, ma) + ".jpg"
            print(index_path)
        except Exception:
            return jsonify({"message": err_500}), 500

        print("okke")
        return send_file(index_path)
