# coding: utf-8
from discord.ext import commands

from utils.my_bot import MyBot


async def after_invoke(ctx: commands.Context):
    ctx.command.reset_cooldown(ctx)


def setup(bot: MyBot):
    bot._after_invoke = after_invoke


def teardown(bot: MyBot):
    bot._after_invoke = None
