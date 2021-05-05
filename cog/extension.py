# coding: utf-8
import traceback
import io

import discord
from discord.ext import commands


class Extension(commands.Cog):
    """
    Permet de gérer les extensions.
    """

    def __init__(self, bot):
        self.bot = bot

    def cog_unload(self):
        pass

    @commands.Cog.listener()
    async def on_ready(self):
        pass

    @commands.is_owner()
    @commands.group(aliases=["ext"])
    async def extension(self, ctx):
        """
        Permet de gérer les extensions.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @commands.is_owner()
    @extension.group(name="reload", invoke_without_command=True)
    async def extension_reload(self, ctx: commands.Context, extension: str):
        """
        Permet de recharger une extension.
        """
        if ctx.invoked_subcommand is None and not extension:
            await ctx.send_help(ctx.command)

        try:
            self.bot.reload_extension(extension)
            await ctx.reply(f"Successfully reloaded extension: `{extension}`")

        except commands.ExtensionNotLoaded:
            await ctx.reply(f"The extension `{extension}` was not loaded.")

        except commands.ExtensionNotFound:
            await ctx.reply(f"The extension `{extension}` was not found.")

        except Exception:
            file = discord.File(io.StringIO(traceback.format_exc()), filename="crash_log.txt")
            await ctx.reply(f"extension reload fail: `{extension}`, rollback", file=file)

    @commands.is_owner()
    @extension_reload.group(name="all")
    async def extension_reload_all(self, ctx):
        """
        Permet de recharger toutes les extensions.
        """
        msg = []

        ext = self.bot.extensions.copy()

        for extension in ext:
            try:
                self.bot.reload_extension(extension)
                msg.append(f"Successfully reloading: `{extension}`")

            except commands.ExtensionNotFound:
                msg.append(f"The extension `{extension}` was not found.")

            except Exception:
                msg.append(f"extension load fail: `{extension}`")
                file = discord.File(io.StringIO(traceback.format_exc()), filename=f"{extension}.txt")
                await ctx.reply(file=file)

        msg.append(f"\nloaded extensions: {len(self.bot.extensions)}/{len(ext)}")
        await ctx.reply("\n".join(msg))

    @commands.is_owner()
    @extension.group(name="unload")
    async def extension_unload(self, ctx, extension: str):
        """
        Permet de décharger une extension.
        """
        if extension == "cog.extension":
            await ctx.reply("You can't unload this extension !")
            return

        try:
            self.bot.unload_extension(extension)
            await ctx.reply(f"Successful extension unloading: `{extension}`")

        except commands.ExtensionNotLoaded:
            await ctx.reply(f"The extension `{extension}` was not loaded.")

    @commands.is_owner()
    @extension.group(name="load")
    async def extension_load(self, ctx, extension: str):
        """
        Permet de charger une extension.
        """
        try:
            self.bot.load_extension(extension)
            await ctx.reply(f"Successful extension loading: `{extension}`")

        except commands.ExtensionNotLoaded:
            ctx.reply(f"The extension `{extension}` was not found.")

        except commands.ExtensionAlreadyLoaded:
            ctx.reply(f"The extension `{extension}` is already loaded.")

        except Exception:
            file = discord.File(io.StringIO(traceback.format_exc()), filename=f"{extension}.txt")
            await ctx.send(f"extension loading fail: `{extension}`", file=file)


def setup(bot):
    bot.add_cog(Extension(bot))
