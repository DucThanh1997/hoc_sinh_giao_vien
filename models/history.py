from db import db
import json as jso


class HistoryModel(db.Model):
    __tablename__ = "history"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    birth_date = db.Column(db.DateTime)
    phone_number = db.Column(db.String(10))
    sex = db.Column(db.String(10))
    address = db.Column(db.String(100))
    native_land = db.Column(db.String(50))
    avatar = db.Column(db.String(200))
    email = db.Column(db.String(80))
    image_name = db.Column(db.String(80))
    job = db.Column(db.Integer)
    # 1: sinh viên
    # 2: giáo viên

    class_id = db.Column(
        db.String(20), db.ForeignKey("class.class_id"), nullable=False
    )
    user_id = db.Column(
        db.String(80), db.ForeignKey("user.user_id"), nullable=False
    )
    school_id = db.Column(
        db.String(20), db.ForeignKey("school.school_id"), nullable=False
    )

    history_1 = db.relationship("ClasssModel")
    history_2 = db.relationship("UserModel")
    history_3 = db.relationship("SchoolModel")

    def __init__(
        self,
        user_id,
        name,
        birth_date,
        phone_number,
        sex,
        address,
        native_land,
        email,
        job,
        class_id,
        school_id,
    ):
        self.user_id = user_id
        self.class_id = class_id
        self.school_id = school_id
        self.name = name
        self.birth_date = birth_date
        self.phone_number = phone_number
        self.sex = sex
        self.address = address
        self.native_land = native_land
        self.email = email
        self.job = job

    def json(self):
        return {
            "user_id ": self.user_id,
            "school_id": self.school_id,
            "class_id": self.class_id,
            "name": self.name,
            "birth_date": str(self.birth_date),
            "phone_number": self.phone_number,
            "sex": self.sex,
            "address": self.address,
            "native_land": self.native_land,
            "email": self.email,
            "avatar": self.avatar,
            "job": self.job,
            "image_name": self.image_name,
        }

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
                res.append(HistoryModel.json(i))
            return jso.loads(jso.dumps(res, default=str))
        else:
            return jso.loads(jso.dumps(HistoryModel.json(data), default=str))

    @classmethod
    def find_by_user_id(cls, user_id):
        user = cls.query.filter_by(user_id=user_id).first()
        return user

    @classmethod
    def find_list_by_name(cls, name, page, per_page):
        user_list = (
            cls.query.filter(cls.name.like("%" + name + "%"))
            .paginate(page, per_page, False)
            .items
        )
        return user_list
