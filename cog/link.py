import logging

import discord
from discord.ext import commands

from utils import regex


logger = logging.getLogger(__file__)


class Link(commands.Cog):
    """
    todo
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        allowed_channels_id = (
            532970830246707251,  # général
            548982055782973461,  # astuce
        )
        if message.channel.id in allowed_channels_id:
            channel = self.bot.get_channel(742516338857213995)  # liens stylés
            if channel is None:
                logger.error("channel 'Liens Stylés' not found !")
                return

            if regex.url_regex.findall(message.content):
                embed = discord.Embed()
                embed.add_field(name="author", value=message.author.mention, inline=False)
                embed.add_field(name="jump", value=f"[jump]({message.jump_url})", inline=False)
                await channel.send(message.content)
                await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Link(bot))
