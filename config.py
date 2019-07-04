import os
import redis

basedir = os.path.abspath(os.path.dirname(__file__))
print(basedir)


class Config(object):
    JWT_SECRET_KEY = "Đố em biết anh đang nghĩ gì"
    SQLALCHEMY_DATABASE_URI = "mysql://root:thanh1997@127.0.0.1/hoc_sinh2"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10Mb

    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    Folder = os.path.join(APP_ROOT, "{}".format("upload"))
    if not os.path.isdir(Folder):
        os.mkdir(Folder)
    UPLOAD_FOLDER = Folder

    redis_host = "localhost"
    redis_port = 6379
    redis_password = ""

    REDIS_CONNECTOR = redis.Redis(host='localhost', port=6379, db=0)
