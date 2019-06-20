from discord import utils
from discord.ext import commands
from discord.ext.commands import Context


class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def emoji(self, ctx: Context, emoji_name: str):
        """Send emoji"""
        emoji = utils.get(self.bot.emojis, name=emoji_name)
        if emoji is not None:
            await ctx.send(emoji)
