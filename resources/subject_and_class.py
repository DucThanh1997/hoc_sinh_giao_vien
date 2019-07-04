from flask_restful import reqparse, Resource
from models.subject_and_class import Subject_And_ClassModel
from models.classs import ClasssModel
from models.exam import ExamModel
from models.subject import SubjectModel
from sqlalchemy import exc
from decorators import *
from messenger import *
from datetime import datetime
import datetime
from flask import g


class Subject_And_Class(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("class_id", type=str, required=False)
    parser.add_argument("subject_id", type=str, required=False)
    parser.add_argument(
        "exam_date", type=str, required=True, help=help
    )

    @gv_authenticate
    def post(self):
        data = Subject_And_Class.parser.parse_args()

        if Subject_And_ClassModel.find_row(data["class_id"], data["user_id"]):
            return {"messages": err_duplicate.format("class")}, 400

        # check khóa ngoại
        if SubjectModel.find_by_subject_id(data['subject_id']) is None:
            return {"messages": err_404.format("subject")}, 404
        if ClasssModel.find_by_class_id(data['class_id']) is None:
            return {"messages": err_404.format("class")}, 404

        if datetime.datetime.now() > datetime.datetime.strptime(data["exam_date"], "%Y-%m-%d"):
            return {"messages": "exam date you set is in the past"}, 400

        row = Subject_And_ClassModel(
            class_id=data["class_id"],
            subject_id=data["subject_id"],
            exam_date=datetime.datetime.strptime(data["exam_date"], "%Y-%m-%d"),
        )
        try:
            row.save_to_db()
        except:
            return {"messages": err_500}, 500
        return {"messages": noti_201}, 201

    @gv_authenticate
    def get(self, class_id=None, page=None, per_page=None):
        if request.args.get('page') and request.args.get('per_page') and request.args.get('class_id'):
            page = int(request.args.get('page'))
            class_id = request.args.get('class_id')
            per_page = int(request.args.get('per_page'))
            list_class = Subject_And_ClassModel.find_list_by_class_id(class_id, page, per_page)
            if list_class is None:
                return {"messages": err_404.format("list_class")}, 404
            return {"list": ClasssModel.to_json(list_class), "count ": len(list_class)}, 200

        if class_id is None:
            list = []
            for row in Subject_And_ClassModel.query.paginate(page, per_page, False).items:
                list.append(row.json())
            return {"list": list,
                    "count": len(Subject_And_ClassModel.query.all())}, 200

        if Subject_And_ClassModel.find_by_class_id(class_id):
            list2 = []
            for row in Subject_And_ClassModel.find_by_class_id(class_id):
                list2.append(row.json())
            return {"danh sách lớp": list2}, 200
        return {"messages": err_404.format("class")}, 404

    @gv_authenticate
    def put(self, class_id, subject_id):
        data = Subject_And_Class.parser.parse_args()
        row = Subject_And_ClassModel.find_row(class_id, subject_id)
        if row is None:
            return {"messages": err_404.format("row")}, 404
        else:
            if SubjectModel.find_by_subject_id(data['subject_id']) is None:
                return {"messages": err_404.format("subject")}, 404
            if ClasssModel.find_by_class_id(data['class_id']) is None:
                return {"messages": err_404.format("class")}, 404

            if datetime.datetime.now() > datetime.datetime.strptime(data["exam_date"], "%Y-%m-%d"):
                return {"messages": "exam date you set is in the past"}, 400

            try:
                if data["class_id"]:
                    row.class_id = data["class_id"]
                if data["exam_date"]:
                    row.exam_date = datetime.datetime.strptime(data["exam_date"], "%Y-%m-%d")
                if data["subject_id"]:
                    row.user_id = data["user_id"]
                row.save_to_db()
            except:
                return {"messages": err_500}, 500
        return {"messages": noti_201}, 201

    @gv_authenticate
    def delete(self, class_id, subject_id):
        row = Subject_And_ClassModel.find_row(class_id, subject_id)
        if row is None:
            return {"messages": err_404.format("row")}, 404
        try:
            row.delete_from_db()
        except:
            return {"messages": err_500}, 500
        return {"messages": noti_201}, 201
