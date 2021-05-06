# coding: utf-8
import os
from discord.ext import commands

from cpuinfo import get_cpu_info

from utils.db import db


class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cpu_info = get_cpu_info()
        self.loop.run_until_complete(db.set_bind(os.environ["PG_DNS"]))
