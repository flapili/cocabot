# coding: utf-8
import logging

import discord
from discord.ext import commands


logger = logging.getLogger(__file__)


class UpVote(commands.Cog):
    """
    todo
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        unsub_reaction_id = 783792395585323078

        if payload.emoji.id != unsub_reaction_id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        message = discord.utils.get(self.bot.cached_messages, id=payload.message_id)
        if message is None:
            channel = guild.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)

        for reaction in message.reactions:
            if isinstance(reaction.emoji, (discord.Emoji, discord.PartialEmoji)):
                if reaction.emoji.id == unsub_reaction_id:
                    users = await reaction.users().flatten()
                    if (
                        reaction.count >= 3
                        or discord.utils.get(users, id=269332971587239938)  # cocadmin
                    ) and not discord.utils.get(users, id=783771075636756510):  # cocabot

                        liens_stylles_channel = self.bot.get_channel(742516338857213995)

                        embed = discord.Embed()
                        embed.add_field(
                            name="author", value=message.author.mention, inline=False
                        )
                        embed.add_field(
                            name="jump",
                            value=f"[jump]({message.jump_url})",
                            inline=False,
                        )
                        await liens_stylles_channel.send(message.content)
                        await liens_stylles_channel.send(embed=embed)
                        await message.add_reaction(
                            self.bot.get_emoji(unsub_reaction_id)
                        )


def setup(bot):
    bot.add_cog(UpVote(bot))
