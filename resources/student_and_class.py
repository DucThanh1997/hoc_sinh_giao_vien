from flask_restful import reqparse, Resource
from models.student_and_class import Student_And_ClassModel
from models.classs import ClasssModel
from models.exam import ExamModel
from models.history import HistoryModel
from sqlalchemy import exc
from decorators import *
from messenger import *
from datetime import datetime
import datetime
from flask import g
from models.subject_and_class import Subject_And_ClassModel


class Student_And_Class(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("class_id", type=str, required=False)
    parser.add_argument("user_id", type=str, required=False)

    @gv_authenticate
    def post(self):
        data = Student_And_Class.parser.parse_args()

        if Student_And_ClassModel.find_row(data["class_id"], data["user_id"]):
            return {"messages": err_duplicate.format("class")}, 400
        # check khóa ngoại
        if ClasssModel.find_by_class_id(class_id=data["class_id"]) is None:
            return {"messages": err_404.format("class")}, 404
        if UserModel.find_by_user_id(user_id=data["user_id"]) is None:
            return {"messages": err_404.format("user")}, 404

        row = Student_And_ClassModel(class_id=data["class_id"], user_id=data["user_id"])
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
        if (
            request.args.get("page")
            and request.args.get("per_page")
            and request.args.get("class_id")
        ):
            page = int(request.args.get("page"))
            class_id = request.args.get("username")
            per_page = int(request.args.get("per_page"))
            list_class = Student_And_ClassModel.find_list_by_class_id(
                class_id, page, per_page
            )
            if list_class is None:
                return {"messages": err_404.format("list_class")}, 404
            return (
                {"list": ClasssModel.to_json(list_class), "count ": len(list_class)},
                200,
            )

        if class_id is None:
            list = []
            for row in Student_And_ClassModel.query.paginate(
                page, per_page, False
            ).items:
                list.append(row.json())
            return {"list": list, "count": len(Student_And_ClassModel.query.all())}, 200

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
            ## check khóa ngoại
            classs = ClasssModel.find_by_class_id(class_id=class_id)
            if classs is None:
                return {"messages": err_404.format("class")}, 404
            user = UserModel.find_by_user_id(user_id=user_id)
            if user is None:
                return {"messages": err_404.format("user")}, 404
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
                    data["user_id"]
                    and UserModel.find_by_user_id(data["user_id"]).job == "1"
                ):
                    row.user_id = data["user_id"]
                history.save_to_db()
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
        list = Student_And_ClassModel.find_list_class_by_user_id(user_id)
        list_exam = []
        if (
            UserModel.find_by_user_id(g.user.user_id).job == 2
            or g.user.user_id == user_id
        ):
            for row in list:
                list_subject = Subject_And_ClassModel.find_by_class_id(
                    class_id=row.class_id
                )
                for subject in list_subject:
                    exam = ExamModel.find_by_subject_id(subject_id=subject.subject_id)
                    if exam[0].exam_date > datetime.datetime.now():
                        list_exam.append(exam)
                    elif exam[0].exam_date == datetime.datetime.now() and exam[
                        0
                    ].exam_start_time > datetime.time(datetime.now()):
                        list_exam.append(exam)
            print(list_exam)
            return {"lịch thi": ExamModel.to_json(list_exam)}
        return {"messages": "Không có quyền"}, 403


# thêm condittion ở câu lệnh query bh mệt vl ra r
