from flask_restful import reqparse, Resource
from decorators import *
from config import Config
from messenger import *
from datetime import datetime
import datetime
from models.history import HistoryModel


class History(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "user_id", type=str, required=True, help=help.format("user_id")
    )
    parser.add_argument(
        "school_id", type=str, required=True, help=help.format("school_id")
    )
    parser.add_argument(
        "class_id", type=str, required=True, help=help.format("class_id")
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
        data = History.parser.parse_args()
        if validiate_mail(data["email"]) is None:
            return {"messages": "email wrong form"}, 400

        if validiate_phone_number(data["phone_number"]) is None:
            return {"messages": "phone_number wrong form"}, 400

        history = HistoryModel(
            user_id=data["user_id"],
            class_id=data["class_id"],
            school_id=data["school_id"],
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
            history.save_to_db()
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
            list_user = HistoryModel.find_list_by_username(
                name, page, per_page
            )

            if list_user is None:
                return {"messages": err_404.format("list_user")}, 404

            return (
                {
                    "list": HistoryModel.to_json(list_user),
                    "count ": len(list_user)
                },
                200,
            )

        if user_id is None:
            list = HistoryModel.to_json(
                HistoryModel.query.paginate(page, per_page, False).items
            )
            return {"list": list, "count": len(HistoryModel.query.all())}, 200

        history = HistoryModel.find_by_user_id(user_id)
        if history is None:
            return {"messages": err_404.format("user")}, 404

        return history.json(), 200

    @gv_authenticate
    def put(self, user_id):
        data = History.parser.parse_args()
        history = HistoryModel.find_by_user_id(user_id)
        if history is None:
            return {"messages": err_404}, 404
        else:
            try:
                if data["user_id"]:
                    history.user_id = data["user_id"]
                if data["name"]:
                    history.name = data["name"]
                if data["birthdate"]:
                    history.birth_date = data["birth_date"]
                if data["sex"]:
                    history.sex = data["sex"]
                if data["native_land"]:
                    history.native_land = data["native_land"]
                if data["email"]:
                    history.email = data["email"]
                if data["job"]:
                    history.job = data["job"]
                if data["class_id"]:
                    history.class_id = data["class_id"]
                if data["school_id"]:
                    history.school_id = data["school_id"]
                history.save_to_db()
            except Exception:
                return {"messages": err_500}, 500

        return {"messages": "update successfully"}, 201

    @gv_authenticate
    def delete(self, user_id):
        history = HistoryModel.find_by_user_id(user_id)
        if history is None:
            return {"messages": err_404.format("user")}, 404

        try:
            history.delete()
        except Exception:
            return {"messages": err_500}, 500

        return {"messages": noti_201}, 200
