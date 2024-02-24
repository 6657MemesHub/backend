import os
import argparse
from logging.config import dictConfig


class BaseConfig:
    DEBUG = False
    TESTING = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI")
    SQLALCHEMY_DATABASE_OPTIONS = {"charset": "utf8mb4"}
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_SIZE = 30
    SQLALCHEMY_POOL_TIMEOUT = 30  # 30s
    SQLALCHEMY_POOL_RECYCLE = 60 * 60  # 1 hour
    SQLALCHEMY_ECHO = False


class TestingConfig(DevelopmentConfig):
    pass


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI")
    SQLALCHEMY_DATABASE_OPTIONS = {"charset": "utf8mb4"}
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_SIZE = 30
    SQLALCHEMY_POOL_TIMEOUT = 30  # 30s
    SQLALCHEMY_POOL_RECYCLE = 60 * 60  # 1 hour
    SQLALCHEMY_ECHO = False


ENV = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}


def config_log():
    dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "DEBUG",
                    "formatter": "default",
                },
                "file": {
                    "class": "logging.FileHandler",
                    "filename": os.path.join(
                        os.path.dirname(__file__), "../logs/info.log"
                    ),
                    "level": "INFO",
                    "formatter": "default",
                },
            },
            "root": {"level": "INFO", "handlers": ["console", "file"]},
        }
    )


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("cmd", help="run app command!")
    parser.add_argument("-p", "--port", help="bind port!", type=int)
    return parser.parse_args()


def get_abs_dir(_file_):
    return os.path.abspath(os.path.dirname(_file_))
