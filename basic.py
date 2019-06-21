import asyncio
import math
from random import randint

import typing

import aiohttp
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

    @commands.command()
    async def tranzat(self, ctx: Context):
        """Send a random tranzat"""

        async def send_tranz(message):
            i = math.floor(randint(0, 200)) * 2
            url_tranz = 'https://tranzat.tk/tranzat/custom/tranzat{}.png'.format(i)
            if message is None:
                message = await ctx.send(embed=embed.tranzat_embed(url_tranz))
            else:
                await message.edit(embed=embed.tranzat_embed(url_tranz))
            try:
                def check(r, u):
                    return u == ctx.message.author and r.emoji == u"\U0001F500"

                await message.add_reaction(u"\U0001F500")
                await self.bot.wait_for('reaction_add', timeout=15.0, check=check)
            except asyncio.TimeoutError:
                await message.clear_reactions()
            else:
                await message.clear_reactions()
                await send_tranz(message)

        await send_tranz(None)

    @commands.command()
    async def reverse(self, ctx: Context, url: str):
        """Google reverse search"""
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.post('https://mrisa-app.herokuapp.com/search',
                                        json={'image_url': url, 'resized_images': False}) as r:
                    if r.status == 200:
                        js = await r.json(content_type=None)
                        await ctx.send(embed=embed.reverse_embed(js))
                    else:
                        await ctx.send("J'ai pas réussi à faire mon job")
