from discord import utils
from discord.ext import commands
from discord.ext.commands import Context

from misc import embed
from misc.googleapis import YoutubeAPI

class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def emoji(self, ctx: Context, emoji_name: str):
        """Send emoji"""
        emoji = utils.get(self.bot.emojis, name=emoji_name)
        if emoji is not None:
            await ctx.send(emoji)

    @commands.command()
    async def sub(self, ctx: Context, search: str):
        """Send youtube channel infos"""
        channel = YoutubeAPI().search_channel(search)
        if channel is None:
            return await ctx.send("Pas de chaîne YouTube trouvée.")
        return await ctx.send(embed=embed.channel_embed(channel))
