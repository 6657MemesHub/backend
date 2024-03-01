from sqlalchemy import func
from models import Meme, MemeSchema, Tag, TagSchema
from flask import current_app
from manage import db
import re


memes_schema = MemeSchema(many=True)
meme_schema = MemeSchema()
tags_schema = TagSchema(many=True)


def get_all_tag():
    try:
        tags = Tag.query.all()
        tags_json = tags_schema.dumps(tags)
        current_app.logger.debug(f"all tag: {tags_json}")
        return tags_json
    except Exception as e:
        current_app.logger.debug(f"{e}")
        raise e


# def get_meme_by_tag(tag, page, page_size):
#     try:
#         if tag:
#             memes = Meme.query.filter(Meme.tags.contains(tag)).paginate(
#                 page=page, per_page=page_size, error_out=False
#             )
#         else:
#             memes = Meme.query.paginate(page=page, per_page=page_size, error_out=False)
#         memes_json = memes_schema.dumps(memes.items)
#         current_app.logger.debug(f"tag: {tag}, memes: {memes_json}")
#         return memes_json
#     except Exception as e:
#         current_app.logger.debug(f"{e}")
#         raise e


def get_meme(content, tag, page, page_size):
    try:
        if content and tag:
            memes = Meme.query.filter(
                Meme.content.contains(content), Meme.tags.contains(tag)
            ).paginate(page=page, per_page=page_size, error_out=False)
        elif content:
            memes = Meme.query.filter(Meme.content.contains(content)).paginate(
                page=page, per_page=page_size, error_out=False
            )
        elif tag:
            memes = Meme.query.filter(Meme.tags.contains(tag)).paginate(
                page=page, per_page=page_size, error_out=False
            )
        else:
            memes = Meme.query.paginate(page=page, per_page=page_size, error_out=False)
        memes_json = memes_schema.dumps(memes.items)
        current_app.logger.debug(
            f"get memes, content: {content}, tag: {tag}, memes: {memes_json}"
        )
        return memes_json
    except Exception as e:
        current_app.logger.debug(f"{e}")
        raise e


# def get_meme_count_by_tag(tag):
#     try:
#         if tag:
#             count = Meme.query.filter(Meme.tags.contains(tag)).count()
#         else:
#             count = Meme.query.count()
#         current_app.logger.debug(f"get count of tag: {tag}:{count}")
#         return count
#     except Exception as e:
#         current_app.logger.debug(f"{e}")
#         raise e


def get_meme_count(content, tag):
    try:
        if content and tag:
            count = Meme.query.filter(
                Meme.content.contains(content), Meme.tags.contains(tag)
            ).count()
        elif content:
            count = Meme.query.filter(Meme.content.contains(content)).count()
        elif tag:
            count = Meme.query.filter(Meme.tags.contains(tag)).count()
        else:
            count = Meme.query.count()
        current_app.logger.debug(
            f"get count, content: {content}, tag: {tag}, count: {count}"
        )
        return count
    except Exception as e:
        current_app.logger.debug(f"{e}")
        raise e


def get_random_meme(tag):
    try:
        if tag:
            random_meme = (
                Meme.query.filter_by(review=True)
                .filter(Meme.tags.contains(tag))
                .order_by(func.random())
                .first()
            )
        else:
            random_meme = (
                Meme.query.filter(Meme.tags.contains(tag))
                .order_by(func.random())
                .first()
            )
        meme_json = meme_schema.dumps(random_meme)
        current_app.logger.debug(f"get random meme: {meme_json}")
        return meme_json
    except Exception as e:
        current_app.logger.debug(f"{e}")
        raise e


def submit_meme(meme_json):
    try:
        current_app.logger.debug(f"submit meme: {meme_json}")
        meme = meme_schema.load(meme_json)
        if meme.review:
            raise Exception(f"invalid feild: review={meme.review}")
        if not meme.like == 0:
            raise Exception(f"invalid feild: like={meme.like}")
        pattern = re.compile(r"^[\w\s]+(,[\w\s]+)*$")
        if bool(pattern.match(meme.tags)):
            raise Exception(f"invalid feild: tags={meme.tags}")
        Meme.query.add_entity
        db.session.add(meme)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.debug(f"{e}")
        raise e
    finally:
        db.session.close()


def update_like_meme(like_json):
    id = like_json.get("id")
    db.session.begin()
    try:
        meme = Meme.query.get_or_404(id)
        meme.like += 1
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.debug(f"{e}")
        raise e
    finally:
        db.session.close()


def get_unreview_meme(page, page_size):
    try:
        memes = Meme.query.filter_by(review=False).paginate(
            page=page, per_page=page_size, error_out=False
        )
        memes_json = memes_schema.dumps(memes.items)
        current_app.logger.debug(f"unreview meme: {memes_json}")
        return memes_json
    except Exception as e:
        current_app.logger.debug(f"{e}")
        raise e


def update_review_result(review_json):
    id = review_json.get("id")
    permit = review_json.get("permit")
    db.session.begin()
    try:
        meme = Meme.query.get_or_404(id)
        if permit is None:
            raise Exception(f"invalid feild: permit={permit}")
        if not permit:
            db.session.delete(meme)
            db.session.commit()
            return False
        tags = [tag for tag in review_json.get("tags").split(",") if tag]
        for tag in tags:
            cur_tag = Tag.query.filter_by(tag=tag).first()
            if not cur_tag:
                new_tag = Tag(tag=tag)
                db.session.add(new_tag)
        meme.review = True
        meme.content = review_json.get("content")
        meme.tags = review_json.get("tags")
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        current_app.logger.debug(f"{e}")
        raise e
    finally:
        db.session.close()
