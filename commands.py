import sys
import traceback

from discord import Activity, ActivityType, Guild, Message, utils
from discord.ext import commands
from discord.ext.commands import Context, CommandError

from admin import Admin
from basic import Basic
from misc import settings, log
from speak import Speak
from music_wavelink import Music

bot = commands.Bot(command_prefix=settings.COMMAND_PREFIX)


async def update_presence():
    name = "{} serveurs ({}help)".format(len(bot.guilds), settings.COMMAND_PREFIX)
    await bot.change_presence(activity=Activity(name=name, type=ActivityType.listening, details="Details"))


@bot.command()
async def ping(ctx):
    """Let's play ping pong"""
    await ctx.send('Pong ! {} ms'.format(round(bot.latency, 2)))


@bot.command()
async def merci(ctx):
    """Send 'SIMB'"""
    await ctx.send('SIMB !')


@bot.event
async def on_connect():
    print("Bot is connected !")


@bot.event
async def on_disconnect():
    print("Bot is disconnected !")


@bot.event
async def on_ready():
    print("Bot is ready !")
    await update_presence()


@bot.event
async def on_guild_join(guild: Guild):
    log.info("New Guild : {} !".format(guild.name))
    await update_presence()


@bot.event
async def on_guild_remove(guild: Guild):
    log.info("Guild removed : {} !".format(guild.name))
    await update_presence()


@bot.event
async def on_command_error(ctx: Context, error: CommandError):
    if hasattr(ctx.command, 'on_error'):
        return

    if isinstance(error, commands.UserInputError):
        return await ctx.send_help(ctx.command)

    print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


@bot.listen()
async def on_message(message: Message):
    if message.guild is None and message.author is not bot.user:
        await log.log_dm(message)
    lower = message.content.lower()
    if "aurore" in lower:
        emoji = utils.get(bot.emojis, name='aurtong')
        await message.add_reaction(emoji)


def launch_discord_bot():
    bot.add_cog(Music(bot))
    bot.add_cog(Basic(bot))
    bot.add_cog(Speak(bot))
    bot.add_cog(Admin(bot))
    bot.run(settings.DISCORD_KEY)
