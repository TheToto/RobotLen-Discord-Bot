import asyncio

import random
import typing

from discord import utils, TextChannel, User, Message, Reaction, Emoji, PartialEmoji, Member, Guild, VoiceChannel
from discord.ext import commands
from discord.ext.commands import Context, BadArgument

from misc import embed, settings


class Guilder(commands.Converter):
    async def convert(self, ctx, arg):
        if arg is int:
            raise BadArgument(message="Not a guild (int)")
        guild = ctx.bot.get_guild(arg)
        if guild is None:
            raise BadArgument(message="Not a guild (None)")
        return guild


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx: Context):
        """A local check which applies to all commands in this cog."""
        if ctx.author.id not in settings.TRUSTED_USERS:
            raise commands.NotOwner
        return True

    #  Channels

    @commands.command(name='{}send'.format(settings.COMMAND_PREFIX))
    async def send_message(self, ctx: Context, channel: typing.Optional[TextChannel], *, text: str):
        """Send a message into a channel"""
        channel = channel or ctx.channel
        return await channel.send(text)

    #  Messages

    @commands.command(name='{}edit'.format(settings.COMMAND_PREFIX))
    async def edit_message(self, ctx: Context, channel: typing.Optional[TextChannel], message: typing.Optional[int], *,
                           text: str):
        """Send a message into a channel"""
        message = message or ctx.message
        return await message.edit(content=text)

    @commands.command(name='{}react'.format(settings.COMMAND_PREFIX))
    async def react_message(self, ctx: Context, message: typing.Optional[Message], emoji: typing.Union[Emoji, str]):
        """React to a message"""
        message = message or ctx.message
        return await message.add_reaction(emoji)

    @commands.command(name='{}spamreact'.format(settings.COMMAND_PREFIX))
    async def spamreact_message(self, ctx: Context, message: typing.Optional[Message]):
        """React 20 times to a message with all bot emojis"""
        message = message or ctx.message
        emojis = random.sample(ctx.bot.emojis, 20)
        for emoji in emojis:
            await message.add_reaction(emoji)

    @commands.command(name='{}delete'.format(settings.COMMAND_PREFIX))
    async def delete_message(self, ctx: Context, message: typing.Optional[Message]):
        """Delete a message"""
        message = message or ctx.message
        return await message.delete()

    @commands.command(name='{}clearreact'.format(settings.COMMAND_PREFIX))
    async def react_message(self, ctx: Context, message: typing.Optional[Message]):
        """Clear Reacts of a message"""
        message = message or ctx.message
        return await message.clear_reactions()

    @commands.command(name='{}pin'.format(settings.COMMAND_PREFIX))
    async def pin_message(self, ctx: Context, message: typing.Optional[Message]):
        """Clear Reacts of a message"""
        message = message or ctx.message
        return await message.pin()

    @commands.command(name='{}unpin'.format(settings.COMMAND_PREFIX))
    async def unpin_message(self, ctx: Context, message: typing.Optional[Message]):
        """Clear Reacts of a message"""
        message = message or ctx.message
        return await message.unpin()

    #  Members

    @commands.command(name='{}dm'.format(settings.COMMAND_PREFIX))
    async def send_dm(self, ctx: Context, user: User, *, text: str):
        """Send a DM to user"""
        await user.create_dm()
        await user.send(text)

    @commands.command(name='{}kick'.format(settings.COMMAND_PREFIX))
    async def kick_user(self, ctx: Context, guild: typing.Optional[Guilder], user: User, *, reason: typing.Optional[str]):
        """Kick a user from a guild"""
        guild = guild or ctx.guild
        await guild.kick(user, reason=reason)

    @commands.command(name='{}ban'.format(settings.COMMAND_PREFIX))
    async def ban_user(self, ctx: Context, guild: typing.Optional[Guilder], user: User, *, reason: typing.Optional[str]):
        """Kick a user from a guild"""
        guild = guild or ctx.guild
        await guild.ban(user, reason=reason)

    @commands.command(name='{}unban'.format(settings.COMMAND_PREFIX))
    async def unban_user(self, ctx: Context, guild: typing.Optional[Guilder], user: User, *, reason: typing.Optional[str]):
        """Kick a user from a guild"""
        guild = guild or ctx.guild
        await guild.unban(user, reason=reason)

    @commands.command(name='{}moveto'.format(settings.COMMAND_PREFIX))
    async def moveto_user(self, ctx: Context, guild: typing.Optional[Guilder], user: User, channel: typing.Optional[VoiceChannel]):
        """Kick a user from a guild"""
        guild = guild or ctx.guild
        member = guild.get_member(user.id)
        await member.move_to(channel)

    @commands.command(name='{}nick'.format(settings.COMMAND_PREFIX))
    async def setname_user(self, ctx: Context, guild: typing.Optional[Guilder], user: User, *, name: typing.Optional[str]):
        """Kick a user from a guild"""
        guild = guild or ctx.guild
        member = guild.get_member(user.id)
        await member.edit(nick=name)
