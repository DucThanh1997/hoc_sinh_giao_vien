import os

import redis
import yaml

basedir = os.path.abspath(os.path.dirname(__file__))
print(basedir)

config = yaml.load(open('config.yaml'), Loader=yaml.FullLoader)


class Config(object):
    JWT_SECRET_KEY = config["jwt"]["secret_key"]
    SQLALCHEMY_DATABASE_URI = config["mysql"]["mysql_uri"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10Mb

    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    Folder = os.path.join(APP_ROOT, "{}".format("upload"))
    if not os.path.isdir(Folder):
        os.mkdir(Folder)
    UPLOAD_FOLDER = Folder

    # redis_host = "localhost"
    # redis_port = 6379
    # redis_password = ""

    REDIS_CONNECTOR = redis.Redis(
        host=config["redis"]["host"],
        port=config["redis"]["port"],
        db=0
    )
