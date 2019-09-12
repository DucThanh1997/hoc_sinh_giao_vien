import json as jso

from db import db


class Subject_And_ClassModel(db.Model):
    __tablename__ = "class_and_subject"

    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(
        db.String(20), db.ForeignKey("class.class_id"), nullable=False
    )
    subject_id = db.Column(
        db.String(80), db.ForeignKey("subject.subject_id"), nullable=False
    )
    exam_date = db.Column(db.DateTime)

    class_4 = db.relationship("ClasssModel")
    subject_1 = db.relationship("SubjectModel")

    def __init__(self, class_id, subject_id, exam_date):
        self.class_id = class_id
        self.subject_id = subject_id
        self.exam_date = exam_date

    def json(self):
        return {
            "class_id": self.class_id,
            "subject_id": self.subject_id,
            "exam_date": self.exam_date,
        }

    def to_json(data):
        if type(data) in (tuple, list):
            res = []
            for i in data:
                res.append(Subject_And_ClassModel.json(i))
            return jso.loads(jso.dumps(res, default=str))
        else:
            return jso.loads(
                jso.dumps(Subject_And_ClassModel.json(data), default=str)
            )

    @classmethod
    def find_row(cls, class_id, subject_id):  # vẫn cần giữ
        return cls.query.filter_by(
            class_id=class_id,
            subject_id=subject_id
        ).first()

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id)

    @classmethod
    def find_by_class_id(cls, class_id):
        return cls.query.filter_by(class_id=class_id).all()

    @classmethod
    def find_by_user_id(cls, subject_id):
        return cls.query.filter_by(subject_id=subject_id).all()

    @classmethod
    def find_exam_date_by_class(cls, class_id):
        return cls.query.filter_by(class_id=class_id).with_entities(
            cls.exam_date
        ).all()

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

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
