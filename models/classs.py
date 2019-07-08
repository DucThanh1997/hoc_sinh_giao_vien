from db import db
import json as jso


class ClasssModel(db.Model):
    __tablename__ = "class"

    class_id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(80))
    school_id = db.Column(
        db.String(20), db.ForeignKey("school.school_id"), nullable=False
    )

    class_1 = db.relationship("SchoolModel")
    class_2 = db.relationship("Student_And_ClassModel")
    class_3 = db.relationship("Teacher_And_ClassModel")
    class_4 = db.relationship("Subject_And_ClassModel")
    mark_4 = db.relationship("MarkModel")

    def __init__(self, name, school_id, class_id):
        self.class_id = class_id
        self.name = name
        self.school_id = school_id

    def json(self):
        return {
            "class_id": self.class_id,
            "name": self.name,
            "school_id": self.school_id,
        }

    def to_json(data):
        if type(data) in (tuple, list):
            res = []
            for i in data:
                res.append(ClasssModel.json(i))
            return jso.loads(jso.dumps(res, default=str))
        else:
            return jso.loads(jso.dumps(ClasssModel.json(data), default=str))

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_by_class_id(cls, class_id):
        return cls.query.filter_by(class_id=class_id).first()

    @classmethod
    def find_all(cls):
        return cls.query.all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_list_by_name(cls, name, page, per_page):
        school_list = (
            cls.query.filter(cls.name.like("%" + name + "%"))
            .paginate(page, per_page, False)
            .items
        )
        return school_list
