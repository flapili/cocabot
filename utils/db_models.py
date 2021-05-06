from utils.db import db


class Message(db.Model):
    __tablename__ = "message"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True, nullable=False)
    author_id = db.Column(db.BigInteger, index=True, nullable=False)
    channel_id = db.Column(db.BigInteger, index=True, nullable=False)
    guild_id = db.Column(db.BigInteger, index=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
