from flask_restful import reqparse, Resource
from models.student_and_class import Student_And_ClassModel
from models.classs import ClasssModel
from models.exam import ExamModel
from sqlalchemy import exc
from decorators import *
from messenger import *
from datetime import datetime
import datetime
from flask import g


class Student_And_Class(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("class_id", type=str, required=False)
    parser.add_argument("user_id", type=str, required=False)
    parser.add_argument(
        "exam_date", type=str, required=True, help=help
    )

    @gv_authenticate
    def post(self):
        data = Student_And_Class.parser.parse_args()

        if Student_And_ClassModel.find_row(data["class_id"], data["user_id"]):
            return {"messages": err_duplicate.format("class")}, 400
        if datetime.datetime.now() > datetime.datetime.strptime(data["exam_date"], "%Y-%m-%d"):
            return {"messages": "exam date you set is in the past"}, 400

        # check khóa ngoại
        if ClasssModel.find_by_class_id(class_id=data["class_id"]) is None:
            return {"messages": err_404.format("class")}, 404
        if UserModel.find_by_user_id(user_id=data["user_id"]) is None:
            return {"messages": err_404.format("user")}, 404

        row = Student_And_ClassModel(
            class_id=data["class_id"],
            user_id=data["user_id"],
            exam_date=datetime.datetime.strptime(data["exam_date"], "%Y-%m-%d"),
        )
        if (
            UserModel.find_by_user_id(data["user_id"]).job == 1
        ):  # lấy user rồi xem nó có là sinh viên không
            try:
                row.save_to_db()
            except:
                return {"messages": err_500}, 500
            return {"messages": noti_201}, 201
        return {"messages": "Only user is student can be add to the row"}, 400

    @gv_authenticate
    def get(self, class_id=None, page=None, per_page=None):
        if request.args.get('page') and request.args.get('per_page') and request.args.get('class_id'):
            page = int(request.args.get('page'))
            class_id = request.args.get('username')
            per_page = int(request.args.get('per_page'))
            list_class = Student_And_ClassModel.find_list_by_class_id(class_id, page, per_page)
            if list_class is None:
                return {"messages": err_404.format("list_class")}, 404
            return {"list": ClasssModel.to_json(list_class), "count ": len(list_class)}, 200

        if class_id is None:
            list = []
            for row in Student_And_ClassModel.query.paginate(page, per_page, False).items:
                list.append(row.json())
            return {"list": list,
                    "count": len(Student_And_ClassModel.query.all())}, 200

        if Student_And_ClassModel.find_by_class_id(class_id):
            list2 = []
            for row in Student_And_ClassModel.find_by_class_id(class_id):
                list2.append(row.json())
            return {"danh sách lớp": list2}, 200
        return {"messages": err_404.format("class")}, 404

    @gv_authenticate
    def put(self, class_id, user_id):
        data = Student_And_Class.parser.parse_args()
        row = Student_And_ClassModel.find_row(class_id, user_id)
        if row is None:
            return {"messages": err_404.format("row")}, 404
        else:
            try:
                exam = ExamModel.find_by_class_id(data['class_id'])
            except:
                return {"messages": err_404.format("exam")}, 404

            if datetime.datetime.now() > datetime.datetime.strptime(data["exam_date"], "%Y-%m-%d"):
                return {"messages": "exam date you set is in the past"}, 400

            # check khóa ngoại
            if ClasssModel.find_by_class_id(class_id=data["class_id"]) is None:
                return {"messages": err_404.format("class")}, 404
            if UserModel.find_by_user_id(user_id=data["user_id"]) is None:
                return {"messages": err_404.format("user")}, 404
            try:
                if data["class_id"]:
                    row.class_id = data["class_id"]
                if data["exam_date"]:
                    row.exam_date = datetime.datetime.strptime(data["exam_date"], "%Y-%m-%d")
                if data["user_id"] and UserModel.find_by_user_id(data["user_id"]).job == "1":
                    row.user_id = data["user_id"]
                row.save_to_db()
            except:
                return {"messages": err_500}, 500
        return {"messages": noti_201}, 201

    @gv_authenticate
    def delete(self, class_id, user_id):
        row = Student_And_ClassModel.find_row(class_id, user_id)
        if row is None:
            return {"messages": err_404.format("row")}, 404
        try:
            row.delete_from_db()
        except:
            return {"messages": err_500}, 500
        return {"messages": noti_201}, 201


class XemLichThi(Resource):
    @token_check
    def get(cls, user_id):
        UserModel.find_by_user_id(g.user.user_id).job
        if UserModel.find_by_user_id(g.user.user_id).chuc_vu == 2 or g.user.user_id == user_id:
            list_date_uncheck = Student_And_ClassModel.find_by_user_id(user_id)
            list_date = []
            for row in list_date_uncheck:
                if row.json()["exam_date"] > datetime.datetime.now():
                    row_2 = row.json()
                    row_2["exam_date"] = row.json()["exam_date"].strftime("%m/%d/%Y, %H:%M:%S")
                    list_date.append(row_2)
            return {"lịch thi": list_date}
        return {"messages": "Không có quyền"}, 403
