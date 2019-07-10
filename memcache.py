from pymemcache.client import base

from models.exam import ExamModel


def get(ma=None):
    if ma is None:
        list = []
        for exam in ExamModel.query.paginate(1, 15, False).items:
            list.append(exam.json())
        return list
    exam = ExamModel.find_by_id(ma)
    if exam is None:
        return {"messages": "không tìm thấy người dùng"}
    return exam.json()


client1 = base.Client(("localhost", 11211))
result = get(1)
print(result)

# if result is None:
#     # The cache is empty, need to get the value
#     # from the canonical source:
#     result = get(1)
#     client1.set('some_key', result)

print(" đây là: ", result)
