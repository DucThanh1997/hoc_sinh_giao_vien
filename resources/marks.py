from flask_restful import reqparse, Resource
from decorators import *
from models.marks import MarkModel
from flask_jwt_extended import jwt_required
from messenger import *
from models.user import UserModel
from models.exam import ExamModel
from models.subject import SubjectModel
from models.student_and_class import Student_And_ClassModel
from sqlalchemy import func
from db import db
from flask import session
from datetime import datetime, timedelta
import datetime


class Mark(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "mark", type=int, required=True, help=help.format("mark")
    )
    parser.add_argument(
        "user_id", type=str, required=True, help=help.format("user_id")
    )

    parser.add_argument(
        "subject_id", type=str, required=True, help=help.format("subject_id")
    )

    parser.add_argument(
        "exam_date", type=str, required=True, help=help.format("exam_date")
    )

    parser.add_argument(
        "class_id", type=str, required=True, help=help.format("class_id")
    )

    @gv_authenticate
    def post(self):
        data = Mark.parser.parse_args()
        if MarkModel.find(data["user_id"], data["exam_date"], data["subject_id"]):
            return {"messages": "this row existed"}, 400

        if UserModel.find_by_user_id(data["user_id"]).job != 1:
            return {"messages": "Bạn chỉ gán điểm được cho học sinh"}, 400

        ## check khóa ngoại
        if UserModel.find_by_user_id(user_id=data["user_id"]) is None:
            return {"messages": err_404.format("user")}
        if ExamModel.find_by_exam_date(exam_date=data["exam_date"]) is None:
            return {"messages": err_404.format("exam")}
        if SubjectModel.find_by_subject_id(subject_id=data["subject_id"]) is None:
            return {"messages": err_404.format("subject")}

        mark = MarkModel(
            mark=data["mark"],
            user_id=data["user_id"],
            exam_date=data["exam_date"],
            subject_id=data["subject_id"]
        )
        try:
            mark.save_to_db()
        except:
            return {"messages": err_500}, 500
        return {"messages": noti_201}, 201

    @token_check
    def get(self, mark_id=None, page=None, per_page=None):
        if mark_id is None:
            list = MarkModel.to_json(MarkModel.query.paginate(page, per_page, False).items)
            return {"list": list,
                    "count": len(MarkModel.query.all())}, 200

        mark = MarkModel.find_by_mark_id(mark_id)
        if mark is None:
            return {"messages": err_404.format("mark")}, 404
        return mark.json(), 200

    @gv_authenticate
    def put(self, mark_id):
        data = Mark.parser.parse_args()
        mark = MarkModel.find_by_mark_id(mark_id)
        if mark is None:
            return {"messages": err_404.format("mark")}, 404

        # check khóa ngoại
        if UserModel.find_by_user_id(user_id=data["user_id"]) is None:
            return {"messages": err_404.format(data["user_id"])}
        if ExamModel.find_by_exam_date_and_subject_id(exam_date=data["exam_date"], subject_id=data["subject_id"]) is None:
            return {"messages": "Không tìm thấy có môn bạn tìm vào ngày {0}".format(data["exam_date"])}
        if SubjectModel.find_by_subject_id(subject_id=data["subject_id"]) is None:
            return {"messages": err_404.format(data["subject_id"])}

        if data["mark"]:
            mark.mark = data["mark"]
        if data["exam_id"]:
            mark.exam_id = data["exam_id"]
        if data["subject_id"]:
            mark.subject_id = data["subject_id"]
        if data["user_id"]:
            mark.user_id = data["user_id"]
        try:
            mark.save_to_db()
        except:
            return {"messages": err_500}, 500
        return {"messages": noti_201}, 201

    @gv_authenticate
    def delete(self, mark_id):
        mark = MarkModel.find_by_mark_id(mark_id)
        if mark is None:
            return {"messages": err_404.format("mark")}, 404
        try:
            mark.delete_from_db()
        except:
            return {"messages": err_500}, 500
        return {"messages": noti_201}


class FindMaxScoreBySubject(Resource):
    # @gv_authenticate
    def get(self, subject_id):
        print("123")
        subqry = db.session.query(func.max(MarkModel.mark)).filter(MarkModel.subject_id == subject_id).all()
        print("1234")
        list_user = MarkModel.find_by_mark_and_subject_id(mark=subqry[0][0], subject_id=subject_id).all()
        return{"list_user": MarkModel.to_json(list_user)}


class FindMaxScoreByClass(Resource):
    # @gv_authenticate
    def get(self, class_id):
        print("123")
        subqry = db.session.query(func.max(MarkModel.mark)).filter(MarkModel.class_id == class_id).all()
        print("1234")
        list_user = MarkModel.find_by_mark_and_class_id(mark=subqry[0][0], class_id=class_id).all()
        return{"list_user": MarkModel.to_json(list_user)}


