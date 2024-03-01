import os
from flask import current_app, g, make_response, request
from models.meme import (
    get_all_tag,
    get_meme,
    get_meme_count,
    get_random_meme,
    get_unreview_meme,
    update_like_meme,
    update_review_result,
    submit_meme,
)
from flasgger import Swagger
from flasgger import swag_from
from flask_limiter import Limiter
from config.constants import METHODTYPE, STATUSCODE
from manage import app

swagger = Swagger(app)
secret_key = os.environ.get("ADMIN_PWD")
limiter = Limiter(key_func=lambda: request.headers.get("X-Forwarded-For"), app=app)


@app.before_request
def authenticate_user():
    """
    鉴权钩子
    """
    rule = request.url_rule
    if rule and "admin" in rule.endpoint:
        user_input_password = request.headers.get("Authorization")
        if user_input_password != secret_key:
            current_app.logger.info(
                f"Access denied, from: {request.headers.get('X-Forwarded-For')}"
            )
            return make_response("Access denied", STATUSCODE.UNAUTHORIZED)
        current_app.logger.info(
            f"Access cuccess, from: {request.headers.get('X-Forwarded-For')}"
        )
        g.user_authenticated = True


@app.route("/all_tag", methods=[METHODTYPE.GET])
@limiter.limit("1 per second")
@swag_from("./swagger/all_tag.yml")
def all_tag():
    """
    获取所有tag
    """
    try:
        tags = get_all_tag()
    except Exception as e:
        return make_response(f"{e}", STATUSCODE.FAIL)
    return make_response(tags, STATUSCODE.SUCCESS)


# @app.route("/meme_by_tag", methods=[METHODTYPE.GET])
# @limiter.limit("1 per second")
# @swag_from("./swagger/meme_by_tag.yml")
# def meme_by_tag():
#     """
#     根据tag获取烂梗
#     """
#     try:
#         tag = request.args["tag"]
#         page = int(request.args["page"])
#         page_size = int(request.args["page_size"])
#         memes = get_meme_by_tag(tag, page, page_size)
#     except Exception as e:
#         return make_response(f"{e}", STATUSCODE.FAIL)
#     return make_response(memes, STATUSCODE.SUCCESS)


@app.route("/meme_search", methods=[METHODTYPE.GET])
@limiter.limit("1 per second")
@swag_from("./swagger/meme_search.yml")
def meme_search():
    """
    烂梗搜索
    """
    try:
        content = request.args["content"]
        tag = request.args["tag"]
        page = int(request.args["page"])
        page_size = int(request.args["page_size"])
        memes = get_meme(content, tag, page, page_size)
    except Exception as e:
        return make_response(f"{e}", STATUSCODE.FAIL)
    return make_response(memes, STATUSCODE.SUCCESS)


# @app.route("/meme_count_by_tag", methods=[METHODTYPE.GET])
# @limiter.limit("1 per second")
# @swag_from("./swagger/meme_count_by_tag.yml")
# def meme_count_by_tag():
#     """
#     根据tag获取烂梗总数
#     """
#     try:
#         tag = request.args["tag"]
#         count = get_meme_count_by_tag(tag)
#     except Exception as e:
#         return make_response(f"{e}", STATUSCODE.FAIL)
#     return make_response({tag: count}, STATUSCODE.SUCCESS)


@app.route("/meme_count", methods=[METHODTYPE.GET])
@limiter.limit("1 per second")
@swag_from("./swagger/meme_count.yml")
def meme_count():
    """
    获取烂梗总数
    """
    try:
        content = request.args["content"]
        tag = request.args["tag"]
        count = get_meme_count(content, tag)
    except Exception as e:
        return make_response(f"{e}", STATUSCODE.FAIL)
    return make_response({"count": count}, STATUSCODE.SUCCESS)


@app.route("/random", methods=[METHODTYPE.GET])
@limiter.limit("1 per second")
@swag_from("./swagger/random.yml")
def random():
    """
    获取一条随机烂梗
    """
    try:
        tag = request.args["tag"]
        meme = get_random_meme(tag)
    except Exception as e:
        return make_response(f"{e}", STATUSCODE.FAIL)
    return make_response(meme, STATUSCODE.SUCCESS)


@app.route("/submit", methods=[METHODTYPE.POST])
@limiter.limit("1 per 10 seconds")
@swag_from("./swagger/submit.yml")
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


@app.route("/like", methods=[METHODTYPE.PUT])
@limiter.limit("1 per day")
@swag_from("./swagger/like.yml")
def like():
    """
    点赞
    """
    like_json = request.json
    try:
        update_like_meme(like_json)
    except Exception as e:
        return make_response(f"{e}", STATUSCODE.FAIL)
    return make_response("Update Success!", STATUSCODE.SUCCESS)


@app.route(
    "/meme_review_get", methods=[METHODTYPE.GET], endpoint="admin_meme_review_get"
)
@swag_from("./swagger/meme_review_get.yml")
def meme_review_get():
    """
    获取未审核烂梗
    """
    try:
        page = int(request.args["page"])
        page_size = int(request.args["page_size"])
        memes = get_unreview_meme(page, page_size)
    except Exception as e:
        return make_response(f"{e}", STATUSCODE.FAIL)
    return make_response(memes, STATUSCODE.SUCCESS)


@app.route(
    "/meme_review_put", methods=[METHODTYPE.PUT], endpoint="admin_meme_review_put"
)
@swag_from("./swagger/meme_review_put.yml")
def meme_review_put():
    """
    审核烂梗
    """
    review_json = request.json
    try:
        permit = update_review_result(review_json)
        if not permit:
            return make_response("烂梗已驳回", STATUSCODE.SUCCESS)
    except Exception as e:
        return make_response(f"{e}", STATUSCODE.FAIL)
    return make_response("烂梗已通过", STATUSCODE.SUCCESS)
