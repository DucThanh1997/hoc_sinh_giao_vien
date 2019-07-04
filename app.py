from flask import Flask
from db import db
from flask_jwt_extended import JWTManager
import pymysql
from flask_restful import Api

from resources.user import *
from resources.user_login import *
from resources.classs import *
from resources.exam import *
from resources.student_and_class import *
from resources.teacher_and_class import *
from resources.subject_and_class import *
from resources.subject import *
from resources.school import *
from resources.marks import *
from blacklist import BLACKLIST as BLACK_LIST
from config import Config

pymysql.install_as_MySQLdb()


app = Flask(__name__)
app.config.from_object(Config)
jwt = JWTManager(app)
api = Api(app)


@app.before_first_request
def create_tables():
    print("lalala")
    db.create_all()


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    return decrypted_token["jti"] in BLACK_LIST


api.add_resource(Classs, "/class", "/class/<string:class_id>", "/class/<int:page>/<int:per_page>")

api.add_resource(Exam, "/exam", "/exam/<int:id>", "/exam/<int:page>/<int:per_page>")

api.add_resource(Subject, "/subject", "/subject/<int:ma_mon>", "/class/<int:page>/<int:per_page>")

api.add_resource(School, "/school", "/school/<int:ma_truong>", "/school/<int:page>/<int:per_page>")

api.add_resource(Mark, "/mark", "/mark/<int:ma_diem>")

api.add_resource(User, "/user", "/user/<string:user_id>", "/user/<int:page>/<int:per_page>")
api.add_resource(UserReg, "/regi", "/regi/<string:class_id>/<int:page>/<int:per_page>")
api.add_resource(UserLogin, "/login")
api.add_resource(UserLogout, "/logout")
api.add_resource(TokenRefresh, "/refresh")
api.add_resource(FindMaxScoreBySubject, "/maxscore_subject/<string:subject_id>", )
api.add_resource(FindMaxScoreByClass, "/maxscore_class/<string:class_id>")
api.add_resource(XemLichThi, "/lichthi/<string:ma>")

api.add_resource(
    Student_And_Class,
    "/danhsach_lop",
    "/danhsach_lop/<int:class_id>",
    "/danhsach_lop/<int:class_id>",
    "/danhsach_lop/<int:class_id>/<string:subject_id>",
    "/danhsach_lop/<int:page>/<int:per_page>"
)

api.add_resource(
    Subject_And_Class,
    "/danhsach",
    "/danhsach/<int:class_id>",
    "/danhsach/<int:class_id>",
    "/danhsach/<int:class_id>/<string:user_id>",
    "/danhsach/<int:page>/<int:per_page>"
)


api.add_resource(
    Teacher_And_Class,
    "/teach",
    "/teach/<int:id_lop>/<string:ma>",
    "/teach/<int:id_lop>",
    "/danhsach/<int:page>/<int:per_page>"
)


api.add_resource(
    UploadAva, "/upload/<string:ma>", "/upload/<string:ma>/<string:filename>"
)

if __name__ == "__main__":
    db.init_app(app)
    app.run(port=5000, debug=True)
