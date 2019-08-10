import aiohttp
import typing
from discord import FFmpegPCMAudio
from discord.ext.commands import Context, BadArgument


async def make_request(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            return await r.json(content_type=None)


async def make_post_request(url: str, json):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=json) as r:
            return await r.json(content_type=None)


def play_audio_bytes(guild, bytes):
    filename = "output-{}.ogg".format(guild.id)
    with open(filename, "wb") as file:
        file.write(bytes)
    guild.voice_client.play(FFmpegPCMAudio(filename))


async def get_last_image(ctx: Context, link: typing.Optional[str]):
    if link is None and len(ctx.message.attachments) > 0:
        link = ctx.message.attachments[0].url
    if link is None:
        async for message in ctx.channel.history(limit=5):
            if len(message.attachments) > 0:
                link = message.attachments[0].url
                break
    if link is None:
        raise BadArgument("Image introuvable")
    return link
