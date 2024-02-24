from models import Meme, MemeSchema
from flask import current_app
from manage import db
import re


memes_schema = MemeSchema(many=True)
meme_schema = MemeSchema()


def get_meme_by_tag(tag, page, page_size):
    if tag:
        memes = Meme.query.filter(Meme.tags.contains(tag)).paginate(
            page=page, per_page=page_size, error_out=False
        )
    else:
        memes = Meme.query.paginate(page=page, per_page=page_size, error_out=False)
    memes_json = memes_schema.dumps(memes.items)
    current_app.logger.debug(f"{memes_json}")
    return memes_json


def submit_meme(meme_json):
    try:
        current_app.logger.debug(f"{meme_json}")
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
        current_app.logger.debug(f"{e}")
        raise e


def like_meme(like_json):
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
    memes = Meme.query.filter_by(review=False).paginate(
        page=page, per_page=page_size, error_out=False
    )
    memes_json = memes_schema.dumps(memes.items)
    current_app.logger.debug(f"{memes_json}")
    return memes_json


def review_result_update(review_json):
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
        meme.review = True
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        current_app.logger.debug(f"{e}")
        raise e
    finally:
        db.session.close()
