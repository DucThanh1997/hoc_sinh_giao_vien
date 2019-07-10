from db import db
import json as jso
import datetime

class ExamModel(db.Model):
    __tablename__ = "exam"
    id = db.Column(db.Integer, primary_key=True)
    exam_room = db.Column(db.String(20))
    exam_date = db.Column(db.DateTime)
    exam_start_time = db.Column(db.DateTime)
    exam_time = db.Column(db.Integer)
    subject_id = db.Column(
        db.String(20), db.ForeignKey("subject.subject_id"), nullable=False
    )

    exam_1 = db.relationship("SubjectModel")

    def __init__(self, exam_room, exam_date, exam_start_time, exam_time, subject_id):
        self.exam_room = exam_room
        self.exam_date = exam_date
        self.exam_start_time = exam_start_time
        self.exam_time = exam_time
        self.subject_id = subject_id

    def json(self):
        return {
            "exam_room": self.exam_room,
            "exam_date": self.exam_date.strftime("%d/%m/%Y"),
            "exam_start_time": self.exam_start_time.strftime("%H:%M:%S"),
            "exam_time": self.exam_time,
            "subject_id": self.subject_id,
        }

    def to_json(data):
        if type(data) in (tuple, list):
            res = []
            for i in data:
                res.append(ExamModel.json(i[0]))
            return jso.loads(jso.dumps(res, default=str))
        else:
            return jso.loads(jso.dumps(ExamModel.json(data), default=str))

    def to_json_for_calender(data):
        if type(data) in (tuple, list):
            res = []
            for i in data:
                res.append(ExamModel.json(i[0]))
            return jso.loads(jso.dumps(res, default=str))
        else:
            return jso.loads(jso.dumps(ExamModel.json(data), default=str))

    @classmethod
    def find_by_exam_date_and_subject_id(cls, exam_date, subject_id):
        return cls.query.filter_by(exam_id=exam_date, subject_id=subject_id).all()

    @classmethod
    def find_by_subject_id(cls, subject_id):
        return cls.query.filter_by(subject_id=subject_id).all()

    @classmethod
    def find_all(cls):
        return cls.query.all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
