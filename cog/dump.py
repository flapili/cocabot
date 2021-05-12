# coding: utf-8
import time

import discord
from discord.ext import commands
from sqlalchemy.dialects.postgresql import insert

from utils.db import db
from utils.my_bot import MyBot

from utils.db_models import Guild, GuildTextChannel, User, Member, Message


class Dump(commands.Cog):
    """
    TODO
    """

    def __init__(self, bot: MyBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild is None:
            return

        async with db.transaction():
            for user in (message.author, message.guild.owner):
                # ensure the user and guild owner already exists in the database
                await insert(User).values(
                    id=user.id,
                    username=user.name,
                    discriminator=user.discriminator,
                    avatar=user.avatar.key,
                ).on_conflict_do_update(
                    index_elements=[User.id],
                    set_=dict(
                        username=user.name,
                        discriminator=user.discriminator,
                        avatar=user.avatar.key,
                    ),
                ).gino.scalar()

            # ensure the guild already exists in the database
            await insert(Guild).values(
                id=message.guild.id,
                name=message.guild.name,
                icon=message.guild.icon.key,
                owner_id=message.guild.owner_id,
            ).on_conflict_do_update(
                index_elements=[Guild.id],
                set_=dict(
                    name=message.guild.name,
                    icon=message.guild.icon.key,
                    owner_id=message.guild.owner_id,
                ),
            ).gino.scalar()

            # ensure the member already exists in the database
            await insert(Member).values(
                user_id=message.author.id,
                guild_id=message.guild.id,
                display_name=message.author.display_name,
                joined_at=message.author.joined_at.replace(tzinfo=None),
            ).on_conflict_do_update(
                index_elements=[Member.user_id, Member.guild_id],
                set_=dict(
                    display_name=message.author.display_name,
                    joined_at=message.author.joined_at.replace(tzinfo=None),
                ),
            ).gino.status()

            # ensure the channel already exists in the database
            await insert(GuildTextChannel).values(
                id=message.channel.id,
                name=message.channel.name,
                guild_id=message.guild.id,
                nsfw=message.channel.is_nsfw(),
            ).on_conflict_do_update(
                index_elements=[GuildTextChannel.id],
                set_=dict(
                    name=message.channel.name,
                    nsfw=message.channel.is_nsfw(),
                ),
            ).gino.scalar()

            # finnaly insert the message
            # (the on_conflict clause in here in case of there is multiples instances of bot running)
            await insert(Message).values(
                id=message.id,
                author_id=message.author.id,
                guild_id=message.guild.id,
                channel_id=message.channel.id,
            ).on_conflict_do_nothing(index_elements=[Message.id]).gino.scalar()

    @commands.group(aliases=["d"])
    @commands.guild_only()
    @commands.is_owner()
    async def dump(self, ctx):
        """
        TODO
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @dump.command(name="guild", aliases=["g"])
    @commands.guild_only()
    @commands.is_owner()
    async def dump_guild(self, ctx: commands.Context):
        """
        Dump tous les membres de la guilde dans une base de donnée.
        """
        counter = 0
        start = time.time()
        async with ctx.typing():
            async with db.transaction():

                # ensure the owner of the guild already exists in the database
                await insert(User).values(
                    id=ctx.guild.owner.id,
                    username=ctx.guild.owner.name,
                    discriminator=ctx.guild.owner.discriminator,
                    avatar=ctx.guild.owner.avatar.key,
                ).on_conflict_do_update(
                    index_elements=[User.id],
                    set_=dict(
                        username=ctx.guild.owner.name,
                        discriminator=ctx.guild.owner.discriminator,
                        avatar=ctx.guild.owner.avatar.key,
                    ),
                ).gino.scalar()

                # ensure the guild already exists in the database
                await insert(Guild).values(
                    id=ctx.guild.id,
                    name=ctx.guild.name,
                    icon=ctx.guild.icon.key,
                    owner_id=ctx.guild.owner_id,
                ).on_conflict_do_update(
                    index_elements=[Guild.id],
                    set_=dict(
                        name=ctx.guild.name,
                        icon=ctx.guild.icon.key,
                        owner_id=ctx.guild.owner_id,
                    ),
                ).gino.scalar()

                for member in ctx.guild.members:
                    # ensure the user already exists in the database
                    await insert(User).values(
                        id=member.id,
                        username=member.name,
                        discriminator=member.discriminator,
                        avatar=member.avatar.key,
                    ).on_conflict_do_update(
                        index_elements=[User.id],
                        set_=dict(
                            username=member.name,
                            discriminator=member.discriminator,
                            avatar=member.avatar.key,
                        ),
                    ).gino.scalar()

                    # finnaly add the member
                    await insert(Member).values(
                        user_id=member.id,
                        guild_id=member.guild.id,
                        display_name=member.display_name,
                        joined_at=member.joined_at.replace(tzinfo=None),
                    ).on_conflict_do_update(
                        index_elements=[Member.user_id, Member.guild_id],
                        set_=dict(
                            display_name=member.display_name,
                            joined_at=member.joined_at.replace(tzinfo=None),
                        ),
                    ).gino.scalar()
                    counter += 1

            await ctx.reply(f"dump guild fini, {counter} membres en {time.time()-start:.3f}s")

    @dump.command(name="messages", aliases=["msg"])
    @commands.guild_only()
    @commands.is_owner()
    async def dump_messages(self, ctx: commands.Context):
        """
        Dump tous les membres de la guilde dans une base de donnée.
        """
        counter = 0
        start = time.time()
        user_cache = set()
        async with ctx.typing():
            async with db.transaction():

                # ensure the guild owner exists in the database
                await insert(User).values(
                    id=ctx.guild.owner.id,
                    username=ctx.guild.owner.name,
                    discriminator=ctx.guild.owner.discriminator,
                    avatar=ctx.guild.owner.avatar.key,
                ).on_conflict_do_update(
                    index_elements=[User.id],
                    set_=dict(
                        username=ctx.guild.owner.name,
                        discriminator=ctx.guild.owner.discriminator,
                        avatar=ctx.guild.owner.avatar.key,
                    ),
                ).gino.scalar()
                user_cache.add(ctx.guild.owner_id)

                # ensure the guild already exists in the database
                await insert(Guild).values(
                    id=ctx.guild.id,
                    name=ctx.guild.name,
                    icon=ctx.guild.icon.key,
                    owner_id=ctx.guild.owner_id,
                ).on_conflict_do_update(
                    index_elements=[Guild.id],
                    set_=dict(
                        name=ctx.guild.name,
                        icon=ctx.guild.icon.key,
                        owner_id=ctx.guild.owner_id,
                    ),
                ).gino.scalar()

                for channel in ctx.guild.text_channels:
                    try:
                        await insert(GuildTextChannel).values(
                            id=channel.id,
                            name=channel.name,
                            guild_id=channel.guild.id,
                            nsfw=channel.is_nsfw(),
                        ).on_conflict_do_update(
                            index_elements=[GuildTextChannel.id],
                            set_=dict(
                                name=channel.name,
                                guild_id=channel.guild.id,
                                nsfw=channel.is_nsfw(),
                            ),
                        ).gino.scalar()
                        async for message in channel.history(limit=None):
                            # ensure the user exists on the database
                            if message.author.id not in user_cache:
                                await insert(User).values(
                                    id=message.author.id,
                                    username=message.author.name,
                                    discriminator=message.author.discriminator,
                                    avatar=message.author.avatar.key,
                                ).on_conflict_do_update(
                                    index_elements=[User.id],
                                    set_=dict(
                                        username=message.author.name,
                                        discriminator=message.author.discriminator,
                                        avatar=message.author.avatar.key,
                                    ),
                                ).gino.scalar()
                                user_cache.add(message.author.id)
                                if isinstance(message.author, discord.Member):
                                    await insert(Member).values(
                                        user_id=message.author.id,
                                        guild_id=message.author.guild.id,
                                        display_name=message.author.display_name,
                                        joined_at=message.author.joined_at.replace(tzinfo=None),
                                    ).on_conflict_do_update(
                                        index_elements=[Member.user_id, Member.guild_id],
                                        set_=dict(
                                            display_name=message.author.display_name,
                                            joined_at=message.author.joined_at.replace(tzinfo=None),
                                        ),
                                    ).gino.scalar()

                            await insert(Message).values(
                                id=message.id,
                                author_id=message.author.id,
                                guild_id=message.guild.id,
                                channel_id=message.channel.id,
                            ).on_conflict_do_nothing(index_elements=[Message.id]).gino.scalar()

                            counter += 1
                    except discord.Forbidden:
                        continue
            await ctx.reply(f"dump messages fini, {counter:,} messages en {time.time()-start:.3f}s")


def setup(bot: MyBot):
    bot.add_cog(Dump(bot))
