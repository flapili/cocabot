# coding: utf-8
import datetime
import typing
import io
import json

import discord
from discord.ext import commands

import numpy

from matplotlib.figure import Figure
from matplotlib.dates import AutoDateLocator, DateFormatter
from matplotlib.ticker import FuncFormatter

from utils import converter


class Stats(commands.Cog):
    """
    Permet d'avoir diverses statistiques.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=["stats", "s"])
    # @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def statistiques(self, ctx):
        """
        Permet d'avoir diverses statistiques sur :
        - le nombre de messages d'un membre
        | dans un channel
        | en général
        - le nombre de message
        | en général
        | dans un channel
        - le membre le plus actif
        | dans un channel
        | en général
        - le message ayant le plus de réactions
        | dans un channel
        | en général
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @statistiques.command(name="reactions", aliases=["r"])
    @commands.cooldown(1, 60, commands.BucketType.member)
    async def statistiques_reactions(
        self,
        ctx,
        channel: typing.Optional[discord.TextChannel] = None,
        after: converter.dateparse = datetime.datetime.min,
        before: converter.dateparse = datetime.datetime.max,
    ):
        """
        Retourne le message avec le plus de réactions.
        - [channel] : le channel où rechercher le message (tous les channels de la guilde si aucun précisé).
        - [after] : recherche parmi les messages qui ont été envoyés après cette date.
        - [before] : cherche parmi les messages qui ont été envoyés avant cette date.
        """

        req = """
            SELECT id, channel_id, reactions
            FROM message
            WHERE (created_at BETWEEN :after AND :before)
            AND (guild_id == :guild_id)
            AND (:channel_id == 0 OR :channel_id == channel_id)
            AND (reactions != "[]")
        """

        parameters = {
            "after": after,
            "before": before,
            "channel_id": channel.id if channel else 0,
            "guild_id": ctx.guild.id,
        }

        messages = []
        async with ctx.typing():
            async with self.bot.db.execute(req, parameters) as cursor:
                async for row in cursor:
                    msg_id = row[0]
                    channel_id = row[1]
                    nb_reactions = sum([c for _, c in json.loads(row[2])])
                    messages.append((msg_id, channel_id, nb_reactions))

            messages.sort(key=lambda x: x[-1])
            message = None
            while message is None and messages:
                msg_id, channel_id, _ = messages.pop()

                c = discord.utils.get(ctx.guild.text_channels, id=channel_id)
                if c:
                    message = discord.utils.get(self.bot.cached_messages, id=msg_id)
                    if not message:
                        try:
                            message = await c.fetch_message(msg_id)
                        except discord.NotFound:
                            pass

            if message is None:
                await ctx.send("Aucun message trouvé")
                return

            reactions_list = []
            for r in message.reactions:
                if isinstance(r.emoji, str):
                    emoji_tag = f" {r.emoji} x{r.count} "
                if isinstance(r.emoji, discord.Emoji):
                    emoji_tag = f" <:_:{r.emoji.id}> x{r.count} "
                if isinstance(r.emoji, discord.PartialEmoji):
                    emoji_tag = f" {r.emoji.name} x{r.count} "
                reactions_list.append(emoji_tag)

            embed = discord.Embed()
            embed.add_field(name="Auteur", value=message.author.mention, inline=False)
            embed.add_field(
                name="Message", value=f"[lien]({message.jump_url})", inline=False
            )
            embed.add_field(
                name="Crée le",
                value=message.created_at.strftime("%d/%m/%Y %H:%M"),
                inline=False,
            )
            embed.add_field(name="Channel", value=message.channel.mention, inline=False)
            embed.add_field(
                name="Reactions", value="\n".join(reactions_list), inline=False
            )
            await ctx.send(embed=embed)

    @statistiques.command(name="messages", aliases=["m", "msg"])
    @commands.guild_only()
    @commands.cooldown(1, 60, commands.BucketType.member)
    async def statistiques_messages(
        self,
        ctx,
        member: typing.Optional[discord.Member] = None,
        channel: typing.Optional[discord.TextChannel] = None,
        cumul: typing.Optional[bool] = True,
        after: converter.dateparse = datetime.datetime.min,
        before: converter.dateparse = datetime.datetime.max,
    ):
        """
        Retourne les nombres de messages par jours.
        - [member] : l'auteur des messages (tous les membres de la guilde si aucun précisé).
        - [channel] : le channel où rechercher le message (tous les channels de la guilde si aucun précisé).
        - [cumul] : true/false.
        - [after] : recherche parmi les messages qui ont été envoyés après cette date.
        - [before] : cherche parmi les messages qui ont été envoyés avant cette date.
        """

        def trace_graph():
            x = numpy.array(sorted(messages.keys()))
            y = numpy.array([messages[k] for k in x])
            if cumul:
                y = numpy.cumsum(y)
                nb_msg = numpy.max(y)
            else:
                nb_msg = numpy.sum(y)

            moy_msg = round(nb_msg / ((before - after).days + 1), 2)

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

        req = """
            SELECT created_at
            FROM message
            WHERE (created_at BETWEEN :after AND :before)
            AND (guild_id == :guild_id)
            AND (:channel_id == 0 OR :channel_id == channel_id)
            AND (:author_id == 0 OR :author_id == author_id)
        """

        created_at = channel.created_at if channel else ctx.guild.created_at
        after = after if after > created_at else created_at
        before = (
            before
            if before < datetime.datetime.utcnow()
            else datetime.datetime.utcnow()
        )

        parameters = {
            "after": after.timestamp(),
            "before": before.timestamp(),
            "author_id": member.id if member else 0,
            "channel_id": channel.id if channel else 0,
            "guild_id": ctx.guild.id,
        }

        messages = {}
        async with ctx.typing():
            async with self.bot.db.execute(req, parameters) as cursor:
                async for row in cursor:
                    key = datetime.datetime.utcfromtimestamp(row[0]).date()
                    messages[key] = messages.get(key, 0) + 1

            if messages:
                image_bytes, nb_msg, moy_msg = await self.bot.loop.run_in_executor(
                    None, trace_graph
                )
            else:
                await ctx.send("Trop peu de donnée pour tracer un graphe ...")

            embed = discord.Embed()

            nb_msg = f"{nb_msg:,}".replace(",", " ")
            moy_msg = f"{moy_msg:,}".replace(",", " ")
            embed.add_field(
                name="nombre de messages",
                value=f"{nb_msg} ({moy_msg} / jour)",
                inline=False,
            )

            param = []
            param.append(f"membre : {member.mention if member else 'aucun'}")
            param.append(f"channel : {channel.mention if channel else 'aucun'}")
            param.append(f"après : {after.isoformat()}")
            param.append(f"avant : {before.isoformat()}")
            embed.add_field(name="paramètres", value="\n".join(param), inline=False)

            embed.set_image(url="attachment://result.png")
        await ctx.send(file=discord.File(image_bytes, "result.png"), embed=embed)


def setup(bot):
    bot.add_cog(Stats(bot))
