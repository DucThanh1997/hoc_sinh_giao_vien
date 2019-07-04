from db import db
import json as jso

class SubjectModel(db.Model):
    __tablename__ = "subject"

    subject_id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(80))

    subject_1 = db.relationship("Subject_And_ClassModel")
    mark_3 = db.relationship("MarkModel")
    exam_1 = db.relationship("ExamModel")

    def __init__(self, name, subject_id):
        self.name = name
        self.subject_id = subject_id

    def json(self):
        return {"id": self.subject_id, "name": self.name}

    def to_json(data):
        if type(data) in (tuple, list):
            res = []
            for i in data:
                res.append(SubjectModel.json(i))
            return jso.loads(jso.dumps(res, default=str))
        else:
            return jso.loads(jso.dumps(SubjectModel.json(data), default=str))

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_by_subject_id(cls, subject_id):
        return cls.query.filter_by(subject_id=subject_id).first()

    @classmethod
    def find_all(cls):
        return cls.query.all()

    @classmethod
    def find_list_by_name(cls, name, page, per_page):
        subject_list = cls.query.filter(cls.name.like("%" + name + "%")).paginate(page, per_page, False).items
        return subject_list

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
