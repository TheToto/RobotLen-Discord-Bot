from discord.ext import commands

from misc import settings
from youtube import Music

bot = commands.Bot(command_prefix='>')


@bot.command()
async def ping(ctx):
    await ctx.send('pong')


def launch_discord_bot():
    bot.add_cog(Music(bot))
    bot.run(settings.DISCORD_KEY)
