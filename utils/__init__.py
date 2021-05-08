# coding: utf-8
import datetime

DISCORD_EPOCH = 1420070400000


def id_to_datetime(id: int) -> datetime.datetime:
    timestamp = ((id >> 22) + DISCORD_EPOCH) / 1000
    return datetime.datetime.utcfromtimestamp(timestamp).replace(tzinfo=datetime.timezone.utc)


def datetime_to_id(dt: datetime.datetime, high: bool = False) -> int:
    discord_millis = int(dt.timestamp() * 1000 - DISCORD_EPOCH)
    return (discord_millis << 22) + (2 ** 22 - 1 if high else 0)
