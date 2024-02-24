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


def get_meme_review(page, page_size):
    memes = Meme.query.filter_by(review=False).paginate(
        page=page, per_page=page_size, error_out=False
    )
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
        current_app.logger.info(f"{e}")
        raise e
