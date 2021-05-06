# # coding: utf-8
import time

import discord
from discord.ext import commands
from sqlalchemy.dialects.postgresql import insert

from utils.my_bot import MyBot
from utils.db_models import Message


class Dump(commands.Cog):
    """
    TODO
    """

    def __init__(self, bot: MyBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        await Message.create(
            id=message.id,
            author_id=message.author.id,
            channel_id=message.channel.id,
            guild_id=message.guild.id,
            created_at=message.created_at.replace(tzinfo=None),
        )

    @commands.group(aliases=["d"])
    @commands.guild_only()
    @commands.is_owner()
    async def dump(self, ctx):
        """
        TODO
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @dump.command(name="messages", aliases=["m", "msg"])
    async def dump_messages(self, ctx):
        """
        Dump tous les messages du discord dans une base de donnée.
        """
        counter = 0
        start = time.time()
        async with ctx.channel.typing():
            for channel in ctx.guild.text_channels:
                try:
                    # TODO bulk insert
                    async for m in channel.history(limit=None):
                        counter += 1
                        await insert(Message).values(
                            id=m.id,
                            author_id=m.author.id,
                            channel_id=m.channel.id,
                            guild_id=m.guild.id,
                            created_at=m.created_at.replace(tzinfo=None),
                        ).on_conflict_do_nothing(
                            index_elements=[Message.id]
                        ).gino.status()
                except discord.Forbidden:
                    continue
            await ctx.reply(
                f"dump messages fini, {counter} messages en {int(time.time()-start)}s"
            )


def setup(bot: MyBot):
    bot.add_cog(Dump(bot))
