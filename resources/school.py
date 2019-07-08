from flask_restful import reqparse, Resource
from decorators import gv_authenticate, token_check
from models.school import SchoolModel
from messenger import *
from flask import request


class School(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("name", type=str, required=True, help=help.format("name"))
    parser.add_argument("address", type=str, required=True, help=help.format("address"))
    parser.add_argument("school_id", type=str, required=True, help=help.format("school_id"))

    @gv_authenticate
    def post(self):
        data = School.parser.parse_args()
        if SchoolModel.find_by_name(data["name"]):
            return {"messages": err_duplicate.format("school")}, 400
        school = SchoolModel(**data)
        try:
            school.save_to_db()
        except:
            return {"messages": err_500}, 500
        return {"messages": noti_201}, 201

    @gv_authenticate
    def get(self, school_id=None, page=None, per_page=None):
        if request.args.get('page') and request.args.get('per_page') and request.args.get('class_id'):
            page = int(request.args.get('page'))
            name = request.args.get('username')
            per_page = int(request.args.get('per_page'))
            list_school = SchoolModel.find_list_by_name(name, page, per_page)
            if list_school is None:
                return {"messages": err_404.format("list_school")}, 404
            return {"list": SchoolModel.to_json(list_school), "count ": len(list_school)}, 200

        if school_id is None:
            list = SchoolModel.to_json(SchoolModel.query.paginate(page, per_page, False).items)
            return {"list": list,
                    "count": len(SchoolModel.query.all())}, 200

        school = SchoolModel.find_by_school_id(school_id)
        if school:
            return school.json(), 200
        return {"messages": err_404.format("school")}, 404

    @gv_authenticate
    def put(self, school_id):
        data = School.parser.parse_args()
        school = SchoolModel.find_by_school_id(school_id)
        if school is None:
            return {"messages": err_404.format("school")}, 404
        if data["name"]:
            school.name = data["name"]
        if data["address"]:
            school.address = data["address"]
        try:
            school.save_to_db()
        except:
            return {"messages": err_500}, 500
        return {"messages": noti_201}, 201

    @gv_authenticate
    def delete(self, school_id):
        school = SchoolModel.find_by_school_id(school_id)
        if school is None:
            return {"messages": err_404.format("school")}, 404
        try:
            school.delete_from_db()
        except:
            return {"messages": err_500}, 500
        return {"messages": noti_201}, 201
