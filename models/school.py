from db import db
import json as jso


class SchoolModel(db.Model):
    __tablename__ = "school"

    school_id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    address = db.Column(db.String(100))

    class_1 = db.relationship("ClasssModel")

    def __init__(self, name, address, school_id):
        self.name = name
        self.address = address
        self.school_id = school_id

    def json(self):
        return {"name": self.name, "address": self.address}

    def to_json(data):
        if type(data) in (tuple, list):
            res = []
            for i in data:
                res.append(SchoolModel.json(i))
            return jso.loads(jso.dumps(res, default=str))
        else:
            return jso.loads(jso.dumps(SchoolModel.json(data), default=str))

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_by_school_id(cls, school_id):
        return cls.query.filter_by(school_id=school_id).first()

    @classmethod
    def find_all(cls):
        return cls.query.all()

    @classmethod
    def find_list_by_name(cls, name, page, per_page):
        school_list = (
            cls.query.filter(cls.name.like("%" + name + "%"))
            .paginate(page, per_page, False)
            .items
        )
        return school_list

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
