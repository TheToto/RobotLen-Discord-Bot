import aiohttp
from discord import FFmpegPCMAudio


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
