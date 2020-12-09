# coding: utf-8
import json
import time

import discord
from discord.ext import commands


class Dump(commands.Cog):
    """
    TODO
    """

    def __init__(self, bot):
        self.bot = bot

    async def update_message(self, message):
        if message.guild is None:
            return

        req = """CREATE TABLE IF NOT EXISTS message(
                    id INT PRIMARY KEY NOT NULL,
                    author_id INT NOT NULL,
                    channel_id INT NOT NULL,
                    guild_id INT NOT NULL,
                    created_at INT NOT NULL,
                    reactions TEXT)"""
        await self.bot.db.execute(req)
        parameters = {
            "id": message.id,
            "author_id": message.author.id,
            "channel_id": message.channel.id,
            "guild_id": message.guild.id,
            "created_at": int(message.created_at.timestamp()),
            "reactions": json.dumps(
                [(str(r.emoji), r.count) for r in message.reactions]
            ),
        }
        await self.bot.db.execute(
            """REPLACE INTO message VALUES(:id, :author_id, :channel_id, :guild_id, :created_at, :reactions)""",
            parameters,
        )
        await self.bot.db.commit()

    @commands.Cog.listener()
    async def on_message(self, message):
        await self.update_message(message)

    @commands.group(aliases=["d"])
    @commands.guild_only()
    @commands.check_any(commands.is_owner())
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
            req = """CREATE TABLE IF NOT EXISTS message(
                id INT PRIMARY KEY NOT NULL,
                author_id INT NOT NULL,
                channel_id INT NOT NULL,
                guild_id INT NOT NULL,
                created_at INT NOT NULL,
                reactions TEXT)"""
            await self.bot.db.execute(req)
            for channel in ctx.guild.text_channels:
                try:
                    async for m in channel.history(limit=None):
                        counter += 1
                        parameters = {
                            "id": m.id,
                            "author_id": m.author.id,
                            "channel_id": m.channel.id,
                            "guild_id": m.guild.id,
                            "created_at": int(m.created_at.timestamp()),
                            "reactions": json.dumps(
                                [(str(r.emoji), r.count) for r in m.reactions]
                            ),
                        }
                        await self.bot.db.execute(
                            "REPLACE INTO message VALUES(:id, :author_id, :channel_id, :guild_id, :created_at, :reactions)",  # noqa: E501
                            parameters,
                        )
                except discord.Forbidden:
                    continue

            await self.bot.db.commit()
            await ctx.send(
                f"dump messages fini, {counter} messages en {int(time.time()-start)}s"
            )


def setup(bot):
    bot.add_cog(Dump(bot))
