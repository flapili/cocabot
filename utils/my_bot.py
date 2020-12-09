# coding: utf-8
import aiosqlite
from discord.ext import commands

from cpuinfo import get_cpu_info


class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cpu_info = get_cpu_info()
        self.db = self.loop.run_until_complete(aiosqlite.connect("data.db"))
