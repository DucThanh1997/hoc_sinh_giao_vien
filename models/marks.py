from db import db
import json as jso

class MarkModel(db.Model):
    __tablename__ = "mark"
    mark_id = db.Column(db.String(20), primary_key=True)
    exam_date = db.Column(db.DateTime)
    mark = db.Column(db.Integer)
    user_id = db.Column(db.String(80), db.ForeignKey("user.user_id"), nullable=False)
    subject_id = db.Column(db.String(20), db.ForeignKey("subject.subject_id"), nullable=False)
    class_id = db.Column(db.String(20), db.ForeignKey("class.class_id"), nullable=False)

    mark_2 = db.relationship("UserModel")
    mark_3 = db.relationship("SubjectModel")
    mark_4 = db.relationship("ClasssModel")

    def __init__(self, mark, user_id, subject_id, class_id, exam_date, mark_id):
        self.mark_id = mark_id
        self.exam_date = exam_date
        self.mark = mark
        self.user_id = user_id
        self.subject_id = subject_id
        self.class_id = class_id

    def json(self):
        return {
            "mark_id": self.mark_id,
            "mark": self.mark,
            "user_id": self.user_id,
            "subject_id": self.subject_id,
            "exam_date": self.exam_date,
            "class_id": self.class_id
        }

    def to_json(data):
        if type(data) in (tuple, list):
            res = []
            for info in data:
                res.append(MarkModel.json(info))
            return jso.loads(jso.dumps(res, default=str))
        else:
            return jso.loads(jso.dumps(MarkModel.json(data), default=str))

    @classmethod
    def find(cls, user_id, subject_id, exam_date):
        return cls.query.filter_by(user_id=user_id, subject_id=subject_id, exam_date=exam_date).first()

    @classmethod
    def find_by_subject(cls, subject_id):
        return cls.query.filter_by(subject_id=subject_id)

    def find_by_class(cls, class_id):
        return cls.query.filter_by(class_id=class_id)

    @classmethod
    def find_by_mark_and_subject_id(cls, mark, subject_id):
        return cls.query.filter_by(mark=mark, subject_id=subject_id).limit(10)

    @classmethod
    def find_by_mark_and_class_id(cls, mark, class_id):
        return cls.query.filter_by(mark=mark, class_id=class_id).limit(10)

    @classmethod
    def find_by_mark_id(cls, mark_id):
        return cls.query.filter_by(mark_id=mark_id).first()

    @classmethod
    def find_all(cls):
        return cls.query.all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
