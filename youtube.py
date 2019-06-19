import asyncio
from collections import deque, namedtuple

import discord
import typing
import youtube_dl

from discord.ext import commands

# Suppress noise about console usage from errors
from discord.ext.commands import Context

from misc.embed import queue_embed


youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/worstaudio/worst',
    'extractaudio': True,
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn',
    'before_options': "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def query(cls, keyword, loop=None):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(keyword, download=False))
        return data

    @classmethod
    def create_player(cls, data):
        filename = data['url']
        print(filename)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


Song = namedtuple("Song", "channel player requester")

queues = {}  # type : Dict[discord.Server, Queue]


class Queue:
    def __init__(self, guild):
        self.guild = guild
        self.playing = False
        self.current = None
        self.queue = deque()  # The queue contains items of type Song
        self.skip_votes = set()

    def add(self, data):
        self.queue.append(data)

    def is_playing(self):
        """ Check if the bot is playing music. """
        return self.playing

    def play_next(self, e=None):
        """ Play the next song if there are any. """
        if e is not None:
            print("Error : " + e)

        if not self.queue or not self.guild.voice_client.is_connected():
            self.playing = False
            return

        self.playing = True
        self.current = self.queue.popleft()
        player = YTDLSource.create_player(self.current)
        self.guild.voice_client.play(player, after=self.play_next)

    def skip(self):
        """ Skip the song currently playing. """
        if self.is_playing():
            self.guild.voice_client.stop()

    def clear(self):
        """ Clear the queue """
        self.queue.clear()


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx: Context, *, channel: typing.Optional[discord.VoiceChannel]):
        """Joins a voice channel"""
        if channel is None:
            if ctx.message.author.voice is None:
                await ctx.send("Tu n'es pas dans un salon vocal")
                raise Exception("Not in voice channel")
            channel = ctx.message.author.voice.channel

        if ctx.voice_client is not None and ctx.voice_client.is_connected():
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()

    @commands.command()
    async def leave(self, ctx: Context):
        """Leave a voice channel"""
        if ctx.voice_client is not None:
            return await ctx.voice_client.disconnect()

    @commands.command()
    async def play(self, ctx, *, song: typing.Optional[str]):
        """Streams from a url"""
        if song is None:
            return await self.resume.callback(self, ctx)

        song = song.strip("< >`")
        queue = queues[ctx.message.guild]

        async with ctx.typing():
            search = await YTDLSource.query(song, self.bot.loop)
            if 'entries' in search:
                search = search['entries'][0]

            queue.add(search)
            if queue.is_playing():
                await ctx.send('Ajouté à la queue : {}'.format(search["title"]))
            else:
                await ctx.send('Vous écoutez : {}'.format(search["title"]))
                queue.play_next()

    @commands.command()
    async def pause(self, ctx):
        """Pause the current stream"""
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()

    @commands.command()
    async def resume(self, ctx):
        """Pause the current stream"""
        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()
        else:
            queue = queues[ctx.message.guild]
            queue.play_next()

    @commands.command()
    async def skip(self, ctx):
        queue = queues[ctx.message.guild]
        if not queue.is_playing():
            await ctx.send("Not playing")
        else:
            queue.skip()

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""
        ctx.voice_client.source.volume = volume / 100
        await ctx.send("Changed volume to {}%".format(volume))

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""
        queue = queues[ctx.message.guild]
        queue.clear()
        ctx.voice_client.stop()

    @commands.command()
    async def queue(self, ctx):
        """Display the guild queue"""
        queue = queues[ctx.message.guild]
        await ctx.send(embed=queue_embed(queue))

    @play.before_invoke
    @volume.before_invoke
    @resume.before_invoke
    @pause.before_invoke
    async def ensure_voice(self, ctx):
        await self.ensure_queue(ctx)
        if ctx.voice_client is None:
            await self.join.callback(self, ctx, channel=None)

    @queue.before_invoke
    async def ensure_queue(self, ctx):
        if ctx.message.guild not in queues:
            queues[ctx.message.guild] = Queue(ctx.guild)
