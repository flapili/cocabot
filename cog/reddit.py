# coding: utf-8
import random

import discord
from discord.ext import commands
import aiohttp


# from utils import converter
from utils.converter import reddit_enum


class Reddit(commands.Cog):
    """
    Commandes lié à Reddit.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=["r"])
    @commands.guild_only()
    async def reddit(self, ctx):
        """
        TODO
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @reddit.group(name="random", aliases=["r"])
    @commands.guild_only()
    async def reddit_random(self, ctx):
        """
        TODO
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @reddit_random.command(name="subreddit", aliases=["sub", "s"])
    @commands.cooldown(1, 60, commands.BucketType.member)
    @commands.guild_only()
    async def reddit_random_subreddit(
        self, ctx: commands.Context, subreddit: str, category: reddit_enum = "hot"
    ):
        """
        TODO
        """

        async with ctx.typing():
            async with aiohttp.ClientSession() as ses:
                async with ses.get(
                    f"https://www.reddit.com/r/{subreddit}/{category}.json"
                ) as r:
                    if r.status == 404:
                        await ctx.message.reply(f"subreddit {subreddit} introuvable !")
                        return

                    if r.status == 404:
                        await ctx.message.reply(f"subreddit {subreddit} privé !")
                        return
                    if r.status != 200:
                        await ctx.message.reply(f"Erreur, code HTTP {r.status} !")
                        raise RuntimeError(await r.text())

                    data = await r.json()

                    memes = [
                        m["data"]
                        for m in data["data"]["children"]
                        if m["data"].get("post_hint", None) == "image"
                    ]

                    if not memes:
                        await ctx.send("Aucune image trouvée !")
                        return

                    meme = random.choice(memes)

                    embed = discord.Embed()
                    embed.add_field(
                        name="post link",
                        value=f"https://www.reddit.com{meme['permalink']}",
                        inline=False,
                    )
                    embed.add_field(name="subreddit", value=subreddit, inline=False)
                    embed.add_field(name="titre", value=meme["title"], inline=False)
                    embed.add_field(name="categorie", value=category, inline=False)
                    embed.set_image(url=meme["url"])

                    await ctx.message.reply(embed=embed)


def setup(bot):
    bot.add_cog(Reddit(bot))
