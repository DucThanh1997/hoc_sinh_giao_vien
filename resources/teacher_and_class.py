from flask_restful import reqparse, Resource
from sqlalchemy import exc

from models.teacher_and_class import Teacher_And_ClassModel
from models.user import UserModel
from models.history import HistoryModel
from models.classs import ClasssModel
from decorators import *
from messenger import *


class Teacher_And_Class(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "class_id", type=str, required=True, help=help.format("class_id")
    )
    parser.add_argument(
        "user_id",
        type=str,
        required=True,
        help=help.format("user_id")
    )

    @gv_authenticate
    def post(self):
        data = Teacher_And_Class.parser.parse_args()
        if Teacher_And_ClassModel.find_row(data["class_id"], data["user_id"]):
            return {"messages": err_duplicate.format("class")}, 400
        row = Teacher_And_ClassModel(**data)

        # check khóa ngoại
        if ClasssModel.find_by_class_id(class_id=data["class_id"]) is None:
            return {"messages": err_404.format("class")}, 404

        if UserModel.find_by_user_id(user_id=data["user_id"]) is None:
            return {"messages": err_404.format("user")}, 404

        # lấy user rồi xem nó có là giáo viên không
        if (
            UserModel.find_by_user_id(data["user_id"]).chuc_vu == 2
        ):
            try:
                row.save_to_db()
            except Exception:
                return {"messages": err_500}, 500

            return {"messages": noti_201}, 201

        return {"messages": "Không có quyền"}, 400

    @gv_authenticate
    def get(self, class_id=None, page=None, per_page=None):
        if (
            request.args.get("page") and
            request.args.get("per_page") and
            request.args.get("username")
        ):
            page = int(request.args.get("page"))
            class_id = request.args.get("username")
            per_page = int(request.args.get("per_page"))
            list_class = Teacher_And_ClassModel.find_list_by_user_id(
                class_id, page, per_page
            )
            if list_class is None:
                return {"messages": err_404.format("list_user")}, 404

            return (
                {
                    "list": Teacher_And_ClassModel.to_json(list_class),
                    "count ": len(list_class),
                },
                200,
            )

        if class_id is None:
            list = []
            for row in Teacher_And_ClassModel.query.paginate(
                page, per_page, False
            ).items:
                list.append(row.json())
            return (
                {
                    "list": list,
                    "count": len(Teacher_And_ClassModel.query.all())
                },
                200
            )

        if Teacher_And_ClassModel.find_by_class_id(class_id):
            list2 = []
            for row in Teacher_And_ClassModel.find_by_id_lop(class_id):
                list2.append(row.json())
            return {"danh sách lớp": list2}, 200

        return {"messages": err_duplicate.format("class")}, 400

    @gv_authenticate
    def put(self, class_id, user_id):
        data = Teacher_And_Class.parser.parse_args()

        # check khóa ngoại
        classs = ClasssModel.find_by_class_id(class_id=data["class_id"])
        if classs is None:
            return {"messages": err_404.format("class")}, 404

        user = UserModel.find_by_user_id(user_id=data["user_id"])
        if user is None:
            return {"messages": err_404.format("user")}, 404

        # lấy user rồi xem nó có là giáo viên không
        if (
            UserModel.find_by_user_id(data["user_id"]).chuc_vu == 2
        ):
            row = Teacher_And_ClassModel.find_row(class_id, user_id)
            if row is None:
                return {"messages": err_404.format("row")}, 404
            else:
                try:
                    history = HistoryModel(
                        user_id=user.user_id,
                        class_id=classs.class_id,
                        school_id=classs.school_id,
                        name=user.name,
                        birth_date=user.birth_date,
                        phone_number=user.phone_number,
                        sex=user.sex,
                        address=user.address,
                        native_land=user.native_land,
                        email=user.email,
                        job=user.job,
                    )
                    if data["class_id"]:
                        row.class_id = data["class_id"]

                    if (
                        data["user_id"] and
                        UserModel.find_by_user_id(
                            data["user_id"]
                        ).chuc_vu == "2"
                    ):
                        row.user_id = data["user_id"]
                    else:
                        return {"messages": err_500}, 500
                    history.save_to_db()
                    row.save_to_db()
                except Exception:
                    return {"messages": err_500}, 500

            return {"messages": noti_201}, 201

    @gv_authenticate
    def delete(self, class_id, user_id):
        row = Teacher_And_ClassModel.find_row(class_id, user_id)
        if row is None:
            return {"messages": err_404}, 404
        try:
            row.delete_from_db()
        except Exception:
            return {"messages": err_500}, 500

        return {"messages": noti_201}, 201
