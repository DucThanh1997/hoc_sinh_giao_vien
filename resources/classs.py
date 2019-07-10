from flask_restful import reqparse, Resource
from decorators import gv_authenticate, token_check
from models.classs import ClasssModel
from models.school import SchoolModel
from flask_jwt_extended import jwt_required
from messenger import *
from flask import request


class Classs(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("name", type=str, required=True, help=help.format("name"))
    parser.add_argument(
        "school_id", type=str, required=True, help=help.format("school_id")
    )
    parser.add_argument(
        "class_id", type=str, required=True, help=help.format("class_id")
    )

    @gv_authenticate
    def post(self):
        data = Classs.parser.parse_args()
        if ClasssModel.find_by_name(data["name"]):
            return {"messages": err_duplicate.format("class")}, 400

        # check khóa ngoại
        if SchoolModel.find_by_school_id(school_id=data["school_id"]) is None:
            return {"messages": err_404.format("school")}, 404

        classs = ClasssModel(
            name=data["name"], school_id=data["school_id"], class_id=data["class_id"]
        )

        classs.save_to_db()
        try:
            classs.save_to_db()
        except:
            return {"messages": err_500}, 500
        return {"messages": noti_201}, 201

    @jwt_required
    def get(self, class_id=None, page=None, per_page=None):
        if (
            request.args.get("page")
            and request.args.get("per_page")
            and request.args.get("username")
        ):
            page = int(request.args.get("page"))
            class_id = request.args.get("username")
            per_page = int(request.args.get("per_page"))
            list_class = ClasssModel.find_list_by_name(class_id, page, per_page)
            if list_class is None:
                return {"messages": err_404.format("list_class")}, 404
            return (
                {"list": ClasssModel.to_json(list_class), "count ": len(list_class)},
                200,
            )

        if class_id is None:
            list = ClasssModel.to_json(
                ClasssModel.query.paginate(page, per_page, False).items
            )
            return {"list": list, "count": len(ClasssModel.query.all())}, 200

        classs = ClasssModel.find_by_class_id(class_id)
        if classs is None:
            return {"messages": err_404.format("class")}, 404
        return classs.json(), 200

    @gv_authenticate
    def put(self, class_id):
        data = Classs.parser.parse_args()
        classs = ClasssModel.find_by_class_id(class_id)
        if classs is None:
            return {"messages": err_404.format("class")}, 404
        if data["name"]:
            classs.name = data["name"]
        if data["school_id"]:
            classs.school_id = data["school_id"]
        if SchoolModel.find_by_school_id(school_id=data["school_id"]) is None:
            return {"messages": err_404.format("school")}, 404
        try:
            classs.save_to_db()
        except:
            return {"messages": err_500}, 500
        return {"messages": noti_201}, 201

    @gv_authenticate
    def delete(self, class_id):
        classs = ClasssModel.find_by_class_id(class_id)
        if classs is None:
            return {"messages": err_404.format("class")}, 404
        try:
            classs.delete_from_db()
        except:
            return {"messages": err_500}, 500
        return {"messages": noti_201}, 201
