import asyncio
import time
import discord
import itertools
import re
import sys
import traceback

import typing
import wavelink
from discord.ext import commands
from typing import Union
from misc import settings
from misc.embed import select_music_embed, queue_embed

RURL = re.compile('https?:\/\/(?:www\.)?.+')


class MusicController:

    def __init__(self, bot, guild_id):
        self.bot = bot
        self.guild_id = guild_id

        self.next = asyncio.Event()
        self.queue = asyncio.Queue()

        self.volume = 40

        self.bot.loop.create_task(self.controller_loop())

    async def controller_loop(self):
        await self.bot.wait_until_ready()

        player = self.bot.wavelink.get_player(self.guild_id)
        await player.set_volume(self.volume)

        while True:
            self.next.clear()

            song = await self.queue.get()
            await player.play(song)

            await self.next.wait()


class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.controllers = {}

        if not hasattr(bot, 'wavelink'):
            self.bot.wavelink = wavelink.Client(self.bot)

        self.bot.loop.create_task(self.start_nodes())

    async def start_nodes(self):
        await self.bot.wait_until_ready()

        # Initiate our nodes. For this example we will use one server.
        # Region should be a discord.py guild.region e.g sydney or us_central (Though this is not technically required)
        node = await self.bot.wavelink.initiate_node(host=settings.LAVALINK_HOST,
                                                     port=int(settings.LAVALINK_PORT),
                                                     rest_uri=settings.LAVALINK_URI,
                                                     password=settings.LAVALINK_PASSWORD,
                                                     identifier='TEST',
                                                     region='western_europe')

        # Set our node hook callback
        node.set_hook(self.on_event_hook)

    async def on_event_hook(self, event):
        """Node hook callback."""
        if isinstance(event, (wavelink.TrackEnd, wavelink.TrackException)):
            controller = self.get_controller(event.player)
            controller.next.set()

    def get_controller(self, value: Union[commands.Context, wavelink.Player]):
        if isinstance(value, commands.Context):
            gid = value.guild.id
        else:
            gid = value.guild_id

        try:
            controller = self.controllers[gid]
        except KeyError:
            controller = MusicController(self.bot, gid)
            self.controllers[gid] = controller

        return controller

    async def cog_check(self, ctx):
        """A local check which applies to all commands in this cog."""
        if not ctx.guild:
            raise commands.NoPrivateMessage
        return True

    async def cog_command_error(self, ctx, error):
        """A local error handler for all errors arising from commands in this cog."""
        if isinstance(error, commands.NoPrivateMessage):
            return await ctx.send('Cette commande ne peut pas être utilisée en messages privés.')

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel = None):
        """Connect to a voice channel."""
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                raise discord.DiscordException('Tu n\'est pas dans un salon vocal !')

        player = self.bot.wavelink.get_player(ctx.guild.id)
        await ctx.send(f'Je rejoins **`{channel.name}`** !')
        await player.connect(channel.id)

    @commands.command()
    async def play(self, ctx, *, query: str):
        """Search for and add a song to the Queue."""
        if not RURL.match(query):
            query = f'ytsearch:{query}'

        tracks = await self.bot.wavelink.get_tracks(f'{query}')
        tracks = tracks[:5]
        if not tracks:
            return await ctx.send('Could not find any songs with that query.')

        numbers = [u"\u0030\u20E3", u"\u0031\u20E3", u"\u0032\u20E3", u"\u0033\u20E3", u"\u0034\u20E3", u"\u0035\u20E3"]

        if len(tracks) > 1:
            message = await ctx.send(embed=select_music_embed(tracks))

            def check(r: discord.Reaction, u):
                return u == ctx.message.author and r.message.id == message.id

            try:
                # Launch in backgroun
                async def put_emoji():
                    try:
                        for i in range(len(tracks)):
                            await message.add_reaction(numbers[i])
                        await message.add_reaction(u"\u274C")
                    except discord.NotFound:
                        pass

                asyncio.ensure_future(put_emoji())

                reaction, user = await self.bot.wait_for('reaction_add', timeout=15.0, check=check)
            except asyncio.TimeoutError:
                await message.clear_reactions()
                return await ctx.send("Pas de réponse...")
            else:
                await message.delete()
                if reaction.emoji not in numbers:
                    return
                track = tracks[numbers.index(str(reaction.emoji))]
        else:
            track = tracks[0]

        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.is_connected:
            await ctx.invoke(self.join)

        controller = self.get_controller(ctx)
        await controller.queue.put(track)
        await ctx.send(f'{str(track)} a été ajouté à la queue.')

    @commands.command()
    async def pause(self, ctx):
        """Pause the player."""
        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.current:
            return await ctx.send('Aucune musique n\'est en cours !')

        await ctx.send('Je me pause !')
        await player.set_pause(True)

    @commands.command()
    async def resume(self, ctx):
        """Resume the player from a paused state."""
        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.paused:
            return await ctx.send('Aucune musique n\'est en cours !')

        await ctx.send('C\'est reparti !')
        await player.set_pause(False)

    @commands.command(aliases=['next'])
    async def skip(self, ctx):
        """Skip the currently playing song."""
        player = self.bot.wavelink.get_player(ctx.guild.id)

        if not player.current:
            return await ctx.send('Aucune musique n\'est en cours !')

        await ctx.send('On passe à la suivante !')
        await player.stop()

    @commands.command(aliases=['vol'])
    async def volume(self, ctx, *, vol: typing.Optional[int]):
        """Set the player volume."""
        player = self.bot.wavelink.get_player(ctx.guild.id)
        controller = self.get_controller(ctx)

        if vol is None:
            return await ctx.send(controller.volume)
        vol = max(min(vol, 1000), 0)
        controller.volume = vol

        await ctx.send(f'Volume : `{vol}`')
        await player.set_volume(vol)

    @commands.command(aliases=['np', 'current', 'nowplaying'])
    async def now_playing(self, ctx):
        """Retrieve the currently playing song."""
        player = self.bot.wavelink.get_player(ctx.guild.id)

        if not player.current:
            return await ctx.send('Aucune musique n\'est en cours !')

        controller = self.get_controller(ctx)
        await controller.now_playing.delete()

        controller.now_playing = await ctx.send(f'Musique actuelle : `{player.current}`')

    @commands.command(aliases=['q'])
    async def queue(self, ctx):
        """Retrieve information on the next 5 songs from the queue."""
        player = self.bot.wavelink.get_player(ctx.guild.id)
        controller = self.get_controller(ctx)

        upcoming = list(itertools.islice(controller.queue._queue, 0, 5))

        embed = queue_embed(upcoming, player.current)

        await ctx.send(embed=embed)

    @commands.command(aliases=['disconnect', 'leave'])
    async def stop(self, ctx):
        """Stop and disconnect the player and controller."""
        player = self.bot.wavelink.get_player(ctx.guild.id)

        try:
            del self.controllers[ctx.guild.id]
        except KeyError:
            await player.disconnect()
            return await ctx.send('Rien n\'est en cours !')

        await player.disconnect()
        await ctx.send('À bientôt.', delete_after=20)

    @commands.command(aliases=['replay'])
    async def restart(self, ctx):
        """Restart the music from the beginning."""
        player = self.bot.wavelink.get_player(ctx.guild.id)

        if not player.current:
            return await ctx.send('Aucune musique n\'est en cours !')

        await player.seek(0)

    @commands.command(aliases=['goto'])
    async def seek(self, ctx, *, seek):
        """Seek the current song to hh:mm:ss."""
        player = self.bot.wavelink.get_player(ctx.guild.id)

        if not player.current:
            return await ctx.send('Aucune musique n\'est en cours !')

        splited = seek.split(':')
        if len(splited) == 3:
            res = int(splited[0]) * 3600 + int(splited[1]) * 60 + int(splited[2])
        elif len(splited) == 2:
            res = int(splited[0]) * 60 + int(splited[1])
        elif len(splited) == 1:
            res = int(splited[0])
        else:
            return await ctx.send("Ce n'est pas le bon format. mm:ss")

        await player.seek(int(res) * 1000)
        await ctx.send("Musique à {} sur {}".format(time.strftime('%H:%M:%S', time.gmtime(res)),
                                                    time.strftime('%H:%M:%S', time.gmtime(player.current.duration / 1000))))
