from db import db
import json as jso



class Student_And_ClassModel(db.Model):
    __tablename__ = "class_and_student"

    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.String(20), db.ForeignKey("class.class_id"), nullable=False)
    user_id = db.Column(db.String(80), db.ForeignKey("user.user_id"), nullable=False)

    class_2 = db.relationship("ClasssModel")
    user_1 = db.relationship("UserModel")

    def __init__(self, class_id, user_id, ):
        self.class_id = class_id
        self.user_id = user_id

    def json(self):
        return {
            "class_id": self.class_id,
            "user_id": self.user_id,
        }

    def to_json(data):
        if type(data) in (tuple, list):
            res = []
            for i in data:
                res.append(Student_And_ClassModel.json(i))
            return jso.loads(jso.dumps(res, default=str))
        else:
            return jso.loads(jso.dumps(Student_And_ClassModel.json(data), default=str))

    @classmethod
    def find_row(cls, class_id, user_id):  # vẫn cần giữ
        return cls.query.filter_by(class_id=class_id, user_id=user_id).first()

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id)

    @classmethod
    def find_by_user_id(cls, user_id):
        return cls.query.filter_by(user_id=user_id).all()

    @classmethod
    def find_all(cls):
        return cls.query.all()

    @classmethod
    def find_list_by_class_id(cls, class_id, page, per_page):
        row_list = (
            cls.query.filter(cls.class_id.like("%" + class_id + "%"))
            .paginate(page, per_page, False)
            .items
        )
        return row_list

    @classmethod
    def find_list_class_by_user_id(cls, user_id):
        row_list = cls.query.filter_by(user_id=user_id).all()
        return row_list

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
