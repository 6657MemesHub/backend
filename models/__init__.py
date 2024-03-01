from manage import db, ma


class Meme(db.Model):
    __tablename__ = "meme"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    tags = db.Column(db.Text, nullable=False)
    like = db.Column(db.Integer, nullable=False)
    review = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"<Meme {self.content}>"


class MemeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Meme
        load_instance = True


class Tag(db.Model):
    __tablename__ = "tag"

    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<Tag {self.tag}>"


class TagSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Tag
        load_instance = True
