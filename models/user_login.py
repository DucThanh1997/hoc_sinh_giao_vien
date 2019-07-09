from db import db
from passlib.hash import pbkdf2_sha256 as sha256
import json as jso


class User_LoginModel(db.Model):
    __tablename__ = "user_login"
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(200))
    user_id = db.Column(
        db.String(80),
        db.ForeignKey("user.user_id"),
        nullable=False
    )

    user_login_1 = db.relationship("UserModel")

    def __init__(self, user_id, password, username):
        self.user_id = user_id
        self.username = username
        self.password = password

    def json(self):
        return {"user_id ": self.user_id, "username": self.username}

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def to_json(data):
        if type(data) in (tuple, list):
            res = []
            for i in data:
                res.append(User_LoginModel.json(i))
            return jso.loads(jso.dumps(res, default=str))
        else:
            return jso.loads(
                jso.dumps(User_LoginModel.json(data), default=str)
            )

    @classmethod
    def find_by_user_id(cls, user_id):
        user = cls.query.filter_by(user_id=user_id).first()
        return user

    @classmethod
    def find_by_username(cls, username):
        user = cls.query.filter_by(username=username).first()
        return user

    @classmethod
    def find_list_by_username(cls, username, page, per_page):
        username = (
            cls.query.filter(cls.username.like("%" + username + "%"))
            .paginate(page, per_page, False)
            .items
        )
        return username

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)
