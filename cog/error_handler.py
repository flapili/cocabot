# coding: utf-8
import traceback
import logging
import io

import discord
from discord.ext import commands


logger = logging.getLogger(__file__)


class ErrorHandler(commands.Cog):
    """
    Error handler.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        if isinstance(error, commands.errors.CheckAnyFailure):
            error = error.errors[0]

        if isinstance(
            error,
            (
                commands.MissingPermissions,
                commands.errors.MissingRole,
                commands.errors.NotOwner,
            ),
        ):
            await ctx.send(
                f"Tu n'as pas les droits d'utiliser `{ctx.command}` {ctx.author.mention} !"
            )
            return

        if isinstance(error, commands.errors.CommandOnCooldown):
            if ctx.author.guild_permissions.administrator:
                await ctx.reinvoke()
            else:
                minutes, seconds = divmod(int(error.retry_after), 60)
                hours, minutes = divmod(minutes, 60)
                days, hours = divmod(hours, 24)
                weeks, days = divmod(days, 7)
                units = [
                    (weeks, "semaine(s)"),
                    (days, "jour(s)"),
                    (hours, "heure(s)"),
                    (minutes, "minute(s)"),
                    (seconds, "seconde(s)"),
                ]

                cd = [f"{time} {unit}" for time, unit in units if time]
                cd = (", ".join(cd[:-1]) + " et " + cd[-1]) if len(cd) > 1 else cd[0]
                await ctx.send(
                    f"{ctx.author.mention} la commande\
                     `{ctx.command.qualified_name}` est en cooldown, merci d'attendre {cd}"
                )
            return

        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(f"Argument manquant : {error.param.name}")
            await ctx.send_help(ctx.command)
            return

        if isinstance(error, commands.errors.BadArgument):
            await ctx.send(error)
            return

        if isinstance(error, commands.errors.DisabledCommand):
            await ctx.send(
                f"la commande `{ctx.prefix}{ctx.command}` est désactivée pour la raison suivante :\
                 {getattr(ctx.command, '__original_kwargs__').get('reason', None)}"
            )
            return

        if isinstance(
            error, (commands.errors.CommandNotFound, commands.errors.CheckFailure)
        ):
            return

        crash_log = "".join(
            traceback.format_exception(type(error), error, error.__traceback__)
        )

        # data = aiohttp.FormData()
        # data.add_field(name="data", value=crash_log)

        # async with aiohttp.ClientSession() as ses:
        #     async with ses.post("https://mystb.in/api/pastes", data=data) as resp:
        #         print(resp.status)
        #         print(await resp.read())
        #         if resp.status != 200:
        #             return
        #         result = await resp.json()
        #         url = f"https://mystb.in/{result['id']}"

        embed = discord.Embed()
        embed.add_field(
            name="date",
            value=ctx.message.created_at.strftime("%d/%m/%Y - %H:%M"),
            inline=False,
        )
        embed.add_field(
            name="command name", value=ctx.command.qualified_name, inline=False
        )
        embed.add_field(name="author", value=ctx.author.mention, inline=False)
        embed.add_field(name="author id", value=ctx.author.id, inline=False)
        embed.add_field(name="message", value=ctx.message.content[:1024], inline=False)
        # embed.add_field(name="crash log", value=url)

        file = discord.File(io.StringIO(crash_log), filename="crash_log.txt")
        try:
            await ctx.send(embed=embed, file=file)
        except discord.Forbidden as e:
            logger.error(e)


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
