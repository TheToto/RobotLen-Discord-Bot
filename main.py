import discord
from discord.ext import commands

from . import settings
from . import web

bot = commands.Bot(command_prefix='>')


@bot.command()
async def ping(ctx):
    await ctx.send('pong')

bot.run(settings.DISCORD_KEY)
web.launch_server()
