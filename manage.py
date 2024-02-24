import os
import sys
from config.setting import config_log
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from config import setting


app = Flask(__name__)
CORS(app)

app.config.from_object(setting.ENV.get(os.environ.get("FLASK_ENV", "default")))
app.config["JSON_AS_ASCII"] = False
db = SQLAlchemy(app)
with app.app_context():
    db.create_all()
ma = Marshmallow(app)


def init_env_path(_file_):
    package_dir = os.path.join(os.path.dirname(_file_), "../")
    abs_path = os.path.abspath(package_dir)
    if abs_path not in sys.path:
        print(f"Add {abs_path} to python path")
        sys.path.insert(0, abs_path)


from api.routes import *

init_env_path(__file__)
config_log()
app.run("0.0.0.0", 8080, debug=True)
app.logger.info(f"run server at port 8080")
