from flask_restful import reqparse, Resource
from decorators import gv_authenticate, token_check
from models.subject import SubjectModel
from flask_jwt_extended import jwt_required
from messenger import *
from flask import request


class Subject(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("name", type=str, required=True, help=help.format("name"))
    parser.add_argument(
        "subject_id", type=str, required=True, help=help.format("subject_id")
    )

    @gv_authenticate
    def post(self):
        data = Subject.parser.parse_args()
        if SubjectModel.find_by_name(data["name"]):
            return {"messages": err_duplicate.format("subject")}, 400

        subject = SubjectModel(**data)
        try:
            subject.save_to_db()
        except:
            return {"messages": err_500}, 500
        return {"messages": noti_201}, 201

    @jwt_required
    def get(self, subject_id=None, page=None, per_page=None):
        if (
            request.args.get("page")
            and request.args.get("per_page")
            and request.args.get("username")
        ):
            page = int(request.args.get("page"))
            name = request.args.get("username")
            per_page = int(request.args.get("per_page"))
            list_subject = SubjectModel.find_list_by_name(name, page, per_page)
            if list_subject is None:
                return {"messages": err_404.format("list_subject")}, 404
            return (
                {
                    "list": SubjectModel.to_json(list_subject),
                    "count ": len(list_subject),
                },
                200,
            )

        if subject_id is None:
            list = []
            for subject in SubjectModel.query.paginate(page, per_page, False).items:
                list.append(subject.json())
            return {"list": list, "count": len(SubjectModel.query.all())}, 200

        subject = SubjectModel.find_by_subject_id(subject_id)
        if subject is None:
            return {"messages": err_404.format("subject")}, 404
        return subject.json(), 200

    @gv_authenticate
    def put(self, subject_id):
        data = Subject.parser.parse_args()
        subject = SubjectModel.find_by_subject_id(subject_id)
        if subject is None:
            return {"messages": err_404.format("subject")}, 404
        else:
            try:
                subject.name = data["name"]
                subject.save_to_db()
            except:
                return {"messages": err_500}, 500
        return {"messages": noti_201}

    @gv_authenticate
    def delete(self, subject_id):
        subject = SubjectModel.find_by_subject_id(subject_id)
        if subject is None:
            return {"messages": err_404.format("subject")}, 404
        try:
            subject.delete_from_db()
        except:
            return {"messages": err_500}, 500
        return {"messages": noti_201}, 201
