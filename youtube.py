import asyncio
from collections import deque, namedtuple

import discord
import typing

from discord.ext import commands
from discord.ext.commands import Context

from misc.embed import queue_embed, select_music_embed

from pytube import YouTube

from misc.googleapis import YoutubeAPI

ffmpeg_options = {
    'options': '-vn',
    'before_options': "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
}


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def query(cls, keyword, loop=None):
        loop = loop or asyncio.get_event_loop()
        data = YoutubeAPI().search(keyword)
        return data

    @classmethod
    def create_player(cls, song, volume):
        id = ''
        if 'id' in song.data:
            id = song.data['id']['videoId']
        else:
            id = song.data['resourceId']['videoId']
        stream = YouTube('https://www.youtube.com/watch?v={}'.format(id)).streams.filter(only_audio=True)
        filename = stream.first().url
        print(filename)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=song.data, volume=volume)


Song = namedtuple("Song", "channel data requester")

queues = {}  # type : Dict[discord.Server, Queue]


class Queue:
    def __init__(self, guild):
        self.vol = 0.5
        self.guild = guild
        self.playing = False
        self.current = None
        self.queue = deque()  # The queue contains items of type Song

    def add(self, channel, data, user):
        self.queue.append(Song(channel, data, user))

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
        player = YTDLSource.create_player(self.current, self.vol)
        self.guild.voice_client.play(player, after=self.play_next)

    def skip(self):
        """ Skip the song currently playing. """
        if self.is_playing():
            self.guild.voice_client.stop()

    def clear(self):
        """ Clear the queue """
        self.queue.clear()

    def volume(self, vol):
        self.guild.voice_client.source.volume = vol
        self.vol = vol


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

        if search is None:
            return await ctx.send("Pas de résultats.")

        numbers = [u"\u0030\u20E3", u"\u0031\u20E3", u"\u0032\u20E3", u"\u0033\u20E3", u"\u0034\u20E3", u"\u0035\u20E3"]

        def check(r, u):
            return u == ctx.message.author

        if len(search) > 1:
            message = await ctx.send(embed=select_music_embed(search))
            try:
                # Launch in background
                async def put_emoji():
                    for i in range(len(search)):
                        await message.add_reaction(numbers[i])
                    await message.add_reaction(u"\u274C")
                asyncio.ensure_future(put_emoji())

                reaction, user = await self.bot.wait_for('reaction_add', timeout=15.0, check=check)
            except asyncio.TimeoutError:
                await message.clear_reactions()
                return await ctx.send("Pas de réponse...")
            else:
                await message.delete()
                if reaction.emoji not in numbers:
                    return
                search = search[numbers.index(str(reaction.emoji))]
        else:
            search = search[0]

        queue.add(ctx.message.channel, search, ctx.message.author)
        if queue.is_playing():
            await ctx.send('Ajouté à la queue : {}'.format(search["snippet"]["title"]))
        else:
            await ctx.send('Vous écoutez : {}'.format(search["snippet"]["title"]))
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
    async def volume(self, ctx, volume: typing.Optional[int]):
        """Changes the player's volume"""
        queue = queues[ctx.message.guild]
        if volume is None:
            return await ctx.send("Volume actuel : {}%".format(int(queue.vol * 100)))
        queue.volume(volume / 100)
        await ctx.send("Volume à to {}%".format(volume))

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""
        queue = queues[ctx.message.guild]
        queue.clear()
        ctx.voice_client.stop()

    @commands.command()
    async def restart(self, ctx):
        """Restart the current music"""
        queue = queues[ctx.message.guild]
        if queue.current is None:
            return await ctx.send("Désolé, pas de musique à redémarrer")
        queue.queue.append(queue.current)
        if queue.is_playing():
            queue.skip()
        else:
            queue.play_next()

    @commands.command()
    async def queue(self, ctx):
        """Display the guild queue"""
        queue = queues[ctx.message.guild]
        await ctx.send(embed=queue_embed(queue))

    @play.before_invoke
    @volume.before_invoke
    @resume.before_invoke
    @pause.before_invoke
    @restart.before_invoke
    async def ensure_voice(self, ctx):
        await self.ensure_queue(ctx)
        if ctx.voice_client is None:
            await self.join.callback(self, ctx, channel=None)

    @queue.before_invoke
    async def ensure_queue(self, ctx):
        if ctx.message.guild not in queues:
            queues[ctx.message.guild] = Queue(ctx.guild)

    @commands.Cog.listener()
    async def on_voice_state_update(self, before: discord.Member, after: discord.Member):
        print("lol")
