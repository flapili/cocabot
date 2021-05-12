# coding: utf-8
import datetime

from utils.db import db
from utils import DISCORD_EPOCH


class User(db.Model):
    __tablename__ = "discord_stats_user"

    id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    username = db.Column(db.Text, nullable=False)
    discriminator = db.Column(db.Text, nullable=False)
    avatar = db.Column(db.Text)

    @property
    def created_at(self):
        timestamp = ((self.id >> 22) + DISCORD_EPOCH) / 1000
        return datetime.datetime.utcfromtimestamp(timestamp).replace(tzinfo=datetime.timezone.utc)


class Guild(db.Model):
    __tablename__ = "discord_stats_guild"

    id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    icon = db.Column(db.Text)
    owner_id = db.Column(db.BigInteger, db.ForeignKey("discord_stats_user.id", ondelete="CASCADE"), nullable=False)

    @property
    def created_at(self):
        timestamp = ((self.id >> 22) + DISCORD_EPOCH) / 1000
        return datetime.datetime.utcfromtimestamp(timestamp).replace(tzinfo=datetime.timezone.utc)


class GuildTextChannel(db.Model):
    __tablename__ = "discord_stats_channel"

    id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    guild_id = db.Column(db.BigInteger, db.ForeignKey("discord_stats_guild.id", ondelete="CASCADE"), nullable=False)
    nsfw = db.Column(db.Boolean)

    @property
    def created_at(self):
        timestamp = ((self.id >> 22) + DISCORD_EPOCH) / 1000
        return datetime.datetime.utcfromtimestamp(timestamp).replace(tzinfo=datetime.timezone.utc)


class Member(db.Model):
    __tablename__ = "discord_stats_member"

    id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    user_id = db.Column(
        db.BigInteger, db.ForeignKey("discord_stats_user.id", ondelete="CASCADE"), index=True, nullable=False
    )
    guild_id = db.Column(
        db.BigInteger, db.ForeignKey("discord_stats_guild.id", ondelete="CASCADE"), index=True, nullable=False
    )
    display_name = db.Column(db.Text)
    joined_at = db.Column(db.DateTime, nullable=False)

    _guild_user_uniq = db.UniqueConstraint("user_id", "guild_id")


class Message(db.Model):
    __tablename__ = "discord_stats_message"

    id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    author_id = db.Column(
        db.BigInteger, db.ForeignKey("discord_stats_user.id", ondelete="CASCADE"), index=True, nullable=False
    )
    guild_id = db.Column(
        db.BigInteger, db.ForeignKey("discord_stats_guild.id", ondelete="CASCADE"), index=True, nullable=False
    )
    channel_id = db.Column(
        db.BigInteger, db.ForeignKey("discord_stats_channel.id", ondelete="CASCADE"), index=True, nullable=False
    )

    @property
    def created_at(self):
        timestamp = ((self.id >> 22) + DISCORD_EPOCH) / 1000
        return datetime.datetime.utcfromtimestamp(timestamp).replace(tzinfo=datetime.timezone.utc)
