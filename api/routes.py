import os
from flask import current_app, g, make_response, request
from models.meme import get_meme_by_tag, get_meme_review, submit_meme
from flasgger import Swagger
from flasgger import swag_from

from config.constants import METHODTYPE, STATUSCODE
from manage import app

swagger = Swagger(app)
secret_key = os.environ.get("ADMIN_PWD")


@app.before_request
def authenticate_user():
    """
    鉴权钩子
    """
    rule = request.url_rule
    if rule and "admin" in rule.endpoint:
        user_input_password = request.headers.get("Authorization")
        if user_input_password != secret_key:
            current_app.logger.info(f"Access denied, from: {request.remote_addr}")
            return make_response("Access denied", STATUSCODE.UNAUTHORIZED)
        current_app.logger.info(f"Access cuccess, from: {request.remote_addr}")
        g.user_authenticated = True


@app.route("/meme_by_tag", methods=[METHODTYPE.GET])
@swag_from("./swagger/meme_by_tag.yml")
def meme_by_tag():
    """
    根据tag获取烂梗
    """
    try:
        tag = request.args["tag"]
        page = int(request.args["page"])
        page_size = int(request.args["page_size"])
        memes = get_meme_by_tag(tag, page, page_size)
    except Exception as e:
        return make_response(f"{e}", STATUSCODE.FAIL)
    return make_response(memes, STATUSCODE.SUCCESS)


@app.route("/meme_review", methods=[METHODTYPE.GET], endpoint="admin")
@swag_from("./swagger/meme_review.yml")
def meme_review():
    """
    获取未审核烂梗
    """
    try:
        page = int(request.args["page"])
        page_size = int(request.args["page_size"])
        memes = get_meme_review(page, page_size)
    except Exception as e:
        return make_response(f"{e}", STATUSCODE.FAIL)
    return make_response(memes, STATUSCODE.SUCCESS)


@app.route("/submit_meme", methods=[METHODTYPE.POST])
@swag_from("./swagger/submit_meme.yml")
def submit():
    """
    提交烂梗
    """
    meme_json = request.json
    try:
        submit_meme(meme_json)
    except Exception as e:
        return make_response(f"{e}", STATUSCODE.FAIL)
    return make_response("Submit Success!", STATUSCODE.SUCCESS)
