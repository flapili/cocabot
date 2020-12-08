import logging
import ssl
import itertools

import discord
from discord.ext import commands
import aiohttp

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

        rejected_website = (
            "tenor.com",
            "discord.com/channels",
            "canary.discord.com/channels",
            )

        rejected_url = tuple(
            f"{scheme}://{link}"
            for link, scheme in itertools.product(rejected_website, ("http", "https"))
        )

        if message.channel.id in allowed_channels_id:
            channel = self.bot.get_channel(742516338857213995)  # liens stylés
            if channel is None:
                logger.error("channel 'Liens Stylés' not found !")
                return

            for url in regex.url_regex.findall(message.content):
                print(url[0])
                if url[0].startswith(rejected_url):
                    continue

                try:
                    async with aiohttp.ClientSession() as ses:
                        async with ses.get(url[0]) as resp:
                            if resp.status != 200:
                                continue
                            if resp.content_type.startswith("image/"):
                                continue
                except ssl.SSLError:
                    continue

                embed = discord.Embed()
                embed.add_field(
                    name="author", value=message.author.mention, inline=False
                )
                embed.add_field(
                    name="jump", value=f"[jump]({message.jump_url})", inline=False
                )
                await channel.send(message.content)
                await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Link(bot))
