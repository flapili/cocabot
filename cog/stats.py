# coding: utf-8
import datetime
import typing
import io
import functools

import discord
from discord.ext import commands

import numpy

from matplotlib.figure import Figure
from matplotlib.dates import AutoDateLocator, DateFormatter
from matplotlib.ticker import FuncFormatter

from utils import converter
from utils.db_models import Message


class Stats(commands.Cog):
    """
    Permet d'avoir diverses statistiques.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=["stats", "s"])
    @commands.guild_only()
    async def statistiques(self, ctx):
        """
        Permet d'avoir diverses statistiques sur le Discord
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @statistiques.command(name="messages", aliases=["m", "msg"])
    @commands.guild_only()
    @commands.cooldown(1, 60, commands.BucketType.member)
    async def statistiques_messages(
        self,
        ctx,
        members: commands.Greedy[discord.Member] = None,
        channels: commands.Greedy[discord.TextChannel] = None,
        cumul: typing.Optional[bool] = True,
        after: typing.Optional[converter.dateparse] = None,
        before: typing.Optional[converter.dateparse] = None,
    ):
        """
        Retourne les nombres de messages par jours.
        - [members] : les auteurs des messages (tous les membres de la guilde si aucun précisé).
        - [channels] : les channels où rechercher les messages (tous les channels de la guilde si aucun de précisé).
        - [cumul] : true/false.
        - [after] : recherche parmi les messages qui ont été envoyés après cette date.
        - [before] : recherche parmi les messages qui ont été envoyés avant cette date.
        """

        def trace_graph(messages, cumul, before, after):
            x = numpy.array(sorted(messages))
            y = numpy.array([messages[k] for k in x])
            if cumul is True:
                y = numpy.cumsum(y)
                nb_msg = numpy.max(y)
            else:
                nb_msg = numpy.sum(y)

            moy_msg = round(
                nb_msg
                / ((before.replace(tzinfo=None) - after.replace(tzinfo=None)).days + 1),
                2,
            )

            fig = Figure(figsize=(20, 10))
            ax = fig.subplots()
            ax.plot_date(x, y, linestyle="solid", linewidth=0.5, markersize=0)

            ax.set_xlim(left=numpy.min(x), right=numpy.max(x))
            ax.set_ylim(bottom=numpy.min(y), top=numpy.max(y))

            ax.xaxis.set_major_locator(
                AutoDateLocator(minticks=14, maxticks=14, interval_multiples=False)
            )
            ax.xaxis.set_major_formatter(DateFormatter("%d/%m/%y"))
            ax.xaxis.set_tick_params(rotation=30)

            ax.yaxis.set_major_formatter(
                FuncFormatter(lambda x, p: f"{int(x):,}".replace(",", " "))
            )

            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight")
            buf.seek(0)
            return buf, nb_msg, moy_msg

        async with ctx.typing():
            req = Message.query.where(Message.guild_id == ctx.guild.id)

            if members:
                req = req.where(Message.author_id.in_([m.id for m in members]))

            if channels:
                req = req.where(Message.channel_id.in_([c.id for c in channels]))

            if before is not None:
                req = req.where(Message.created_at.replace(tzinfo=None) <= before)

            if after is not None:
                req = req.where(Message.created_at.replace(tzinfo=None) >= after)

            messages: dict[datetime.date, int] = {}
            for m in await req.gino.all():
                key = m.created_at.date()
                messages[key] = messages.get(key, 0) + 1

            if messages:
                image_bytes, nb_msg, moy_msg = await self.bot.loop.run_in_executor(
                    None,
                    functools.partial(
                        trace_graph,
                        messages,
                        cumul,
                        before or datetime.datetime.utcnow(),
                        after or ctx.guild.created_at.replace(tzinfo=None),
                    ),
                )
            else:
                await ctx.reply("Trop peu de donnée pour tracer un graphe ...")
                return

            embed = discord.Embed()

            nb_msg = f"{nb_msg:,}".replace(",", " ")
            moy_msg = f"{moy_msg:,}".replace(",", " ")
            embed.add_field(
                name="nombre de messages",
                value=f"{nb_msg} ({moy_msg} / jour)",
                inline=False,
            )

            param = []
            param.append(f"membres : {len(members) if members is not None else 'tous'}")
            param.append(
                f"channels : {len(channels) if channels is not None else 'tous'}"
            )
            param.append(
                f"après : {after.isoformat() if after is not None else ctx.guild.created_at.isoformat()}"
            )
            param.append(
                f"après : {before.isoformat() if before is not None else datetime.datetime.utcnow().isoformat()}"
            )
            embed.add_field(name="paramètres", value="\n".join(param), inline=False)

            embed.set_image(url="attachment://result.png")
        await ctx.reply(file=discord.File(image_bytes, "result.png"), embed=embed)


def setup(bot):
    bot.add_cog(Stats(bot))
