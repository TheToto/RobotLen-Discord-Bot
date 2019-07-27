import asyncio
import math
from random import randint

import typing
from discord import utils
from discord.ext import commands
from discord.ext.commands import Context

from misc import embed
from misc.googleapis import YoutubeAPI, CloudVision, Translate
from misc.helpers import make_request, make_post_request


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
    async def reverse(self, ctx: Context, link: typing.Optional[str]):
        """Google reverse search"""
        if link is None and len(ctx.message.attachments) > 0:
            link = ctx.message.attachments[0].url
        if link is None:
            return
        async with ctx.typing():
            js = await make_post_request('https://mrisa-app.herokuapp.com/search',
                                         json={'image_url': link, 'resized_images': False})
            if js is not None:
                await ctx.send(embed=embed.reverse_embed(js))
            else:
                await ctx.send("J'ai pas réussi à faire mon job")

    @commands.command()
    async def wiki(self, ctx: Context, keyword: str):
        """Search on wikipedia"""
        async with ctx.typing():
            js = await make_request("https://fr.wikipedia.org/w/api.php?action=query&list=search&srnamespace=0"
                                    "&srlimit=1&format=json&srsearch={}".format(keyword))
            if js is not None:
                pageid = js['query']['search'][0]['pageid']
                article = await make_request("https://fr.wikipedia.org/w/api.php?format=json&action=query&prop"
                                             "=extracts|pageimages&exintro=&explaintext=&pageids={}".format(pageid))
                for page in article['query']['pages']:
                    return await ctx.send(embed=embed.wiki_embed(article['query']['pages'][page]))
            else:
                await ctx.send("J'ai pas réussi à faire mon job")

    @commands.command()
    async def learn_life(self, ctx: Context):
        """Random article on wikipedia"""
        async with ctx.typing():
            js = await make_request("https://fr.wikipedia.org/w/api.php?action=query&generator=random&grnnamespace=0"
                                    "&format=json")
            if js is not None:
                pageid = next(iter(js['query']['pages']))
                article = await make_request("https://fr.wikipedia.org/w/api.php?format=json&action=query&prop"
                                             "=extracts|pageimages&exintro=&explaintext=&pageids={}".format(pageid))
                for page in article['query']['pages']:
                    return await ctx.send(embed=embed.wiki_embed(article['query']['pages'][page]))
            else:
                await ctx.send("J'ai pas réussi à faire mon job")

    @commands.command()
    async def vision(self, ctx: Context, *, link: typing.Optional[str]):
        """Detect labels of image"""
        if link is None and len(ctx.message.attachments) > 0:
            link = ctx.message.attachments[0].url
        if link is None:
            return
        labels = CloudVision().label(link)
        res = ''
        for label in labels:
            res += '{} : {}%\n'.format(label.description, round(label.score * 100))
        await ctx.send("Je trouve sur cette image : \n{}".format(res))

    @commands.command()
    async def read(self, ctx: Context, *, link: typing.Optional[str]):
        """Perform an OCR of the image"""
        if link is None and len(ctx.message.attachments) > 0:
            link = ctx.message.attachments[0].url
        if link is None:
            return
        text = CloudVision().read(link)
        if text is None:
            return await ctx.send("Je ne peux rien lire sur cette image.")
        await ctx.send("Je lis sur cette image en {} : \n{}".format(text.locale, text.description))

    @commands.command()
    async def translate(self, ctx: Context, *, text: str):
        """Translate the text into french"""
        await ctx.invoke(self.translatein, lang="fr", text=text)

    @commands.command()
    async def translatein(self, ctx: Context, lang: str, *, text: str):
        """Translate the text into `lang`"""
        res = Translate().translate(text, lang)
        await ctx.send("Traduction {} -> {} :\n{}".format(res['detectedSourceLanguage'], lang, res['translatedText']))
