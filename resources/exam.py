from flask_restful import reqparse, Resource
from decorators import gv_authenticate
from models.exam import ExamModel
from models.subject import SubjectModel
from flask_jwt_extended import jwt_required
from messenger import *
from datetime import datetime, timedelta
import datetime


class Exam(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "exam_room", type=str, required=True, help=help.format("exam_room")
    )

    parser.add_argument(
        "exam_date", type=str, required=True, help=help.format("exam_date")
    )

    parser.add_argument(
        "exam_start_time", type=str, required=True, help=help.format("exam_start_time")
    )
    parser.add_argument(
        "exam_time", type=str, required=True, help=help.format("exam_time")
    )
    parser.add_argument(
        "subject_id", type=str, required=True, help=help.format("subject_id")
    )

    @gv_authenticate
    def post(self):
        data = Exam.parser.parse_args()
        if ExamModel.find_by_exam_date_and_subject_id(
            data["exam_date"], data["subject_id"]
        ):
            return {"messages": err_duplicate.format("exam")}, 400
        try:
            exam_date = datetime.datetime.strptime(data["exam_date"], "%Y-%m-%d")
            exam_start_time = datetime.datetime.strptime(
                data["exam_start_time"], "%H-%M"
            )
        except:
            return (
                {
                    "messages": "start date or end date was not valid a date form. Please try again"
                },
                400,
            )

        # check date
        if exam_date > datetime.datetime.now():
            return {"messages": "exam date can't be the day in the past"}, 400

        # check khóa ngoại
        if SubjectModel.find_by_subject_id(subject_id=data["subject_id"]) is None:
            return {"messages": err_404.format("subject")}, 404

        exam = ExamModel(
            exam_room=data["exam_room"],
            exam_date=exam_date,
            exam_start_time=exam_start_time,
            exam_time=data["exam_time"],
            subject_id=data["subject_id"],
        )
        exam.save_to_db()
        try:
            exam.save_to_db()
        except:
            return {"messages": err_500}, 500
        return {"messages": noti_201}, 201

    @jwt_required
    def get(self, exam_date=None, page=None, per_page=None, subject_id=None):
        # in ra tất cả
        if exam_date is None:
            list = ExamModel.to_json(
                ExamModel.query.paginate(page, per_page, False).items
            )
            return {"list": list, "count": len(ExamModel.query.all())}, 200

        # in ra 1 cái chỉ định
        exam = ExamModel.find_by_exam_date_and_subject_id(exam_date, subject_id)
        if exam is None:
            return {"messages": err_404.format("exam")}, 404
        return ExamModel.to_json(exam), 200

    @gv_authenticate
    def put(self, exam_date, subject_id):
        data = Exam.parser.parse_args()
        exam = ExamModel.find_by_exam_date_and_subject_id(exam_date, subject_id)
        if exam is None:
            return {"messages": err_404.format("exam")}, 404
        if data["exam_room"]:
            exam.exam_room = data["exam_room"]
        if data["exam_date"]:
            exam.exam_date = data["exam_date"]
        if data["exam_start_time"]:
            exam.exam_start_time = data["exam_start_time"]
        if data["exam_time"]:
            exam.exam_time = data["exam_time"]
        if data["subject_id"]:
            exam.subject_id = data["subject_id"]

        # check khóa ngoại
        if SubjectModel.find_by_subject_id(subject_id=data["subject_id"]) is None:
            return {"messages": err_404.format("subject")}, 404

        try:
            exam.save_to_db()
        except:
            return {"messages": err_500}, 500
        return {"messages": noti_201}, 201

    @gv_authenticate
    def delete(self, exam_date, subject_id):
        exam = ExamModel.find_by_exam_date_and_subject_id(exam_date, subject_id)
        if exam is None:
            return {"messages": err_404.format("exam")}, 404
        try:
            exam.delete_from_db()
        except:
            return {"messages": err_500}, 500
        return {"messages": noti_201}
