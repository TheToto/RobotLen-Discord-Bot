import discord
from discord.ext import commands
from discord.ext.commands import Context

import youtube
from misc.googleapis import TextToSpeech
from misc.helpers import play_audio_bytes


class Speak(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def speak_tts(guild, sentence, lang=None):
        audio = TextToSpeech().process(sentence, lang)
        if guild.voice_client.is_playing():
            guild.voice_client.stop()
        play_audio_bytes(guild, audio)

    @commands.command()
    async def speak(self, ctx: Context, *, sentence: str):
        """Speak in voice channel"""
        if ctx.voice_client is not None and ctx.voice_client.is_connected():
            Speak.speak_tts(ctx.guild, sentence)
        else:
            await ctx.send("Tu ne m'entendra pas...")

    @commands.command()
    async def speakin(self, ctx: Context, lang: str, *, sentence: str):
        """Speak in voice channel with the specified voice"""
        if ctx.voice_client is not None and ctx.voice_client.is_connected():
            lang = TextToSpeech().choose_voice(lang)
            self.speak_tts(ctx.guild, sentence, lang)
        else:
            await ctx.send("Tu ne m'entendra pas...")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState,
                                    after: discord.VoiceState):
        if before.channel == after.channel or member.bot:
            return
        guild = member.guild
        if not guild.voice_client or not guild.voice_client.is_connected() or guild.voice_client.is_playing():
            return
        if youtube.Queue.get(guild).is_playing():
            return

        voice_channel = guild.voice_client.channel
        if before.channel != voice_channel and after.channel == voice_channel:
            print(member.display_name + " join " + after.channel.name)
            Speak.speak_tts(guild, "{} à rejoint {}".format(member.display_name, after.channel.name))
        if after.channel != voice_channel and before.channel == voice_channel:
            print(member.display_name + " left " + before.channel.name)
            Speak.speak_tts(guild, "{} à quitté {}".format(member.display_name, before.channel.name))

    @speak.before_invoke
    async def ensure_queue(self, ctx):
        if not ctx.guild.voice_client \
                or not ctx.guild.voice_client.is_connected():
            await ctx.send("Tu ne m'entendra pas...")
            raise Exception("Not in voice channel")
        if youtube.Queue.get(ctx.guild).is_playing():
            await ctx.send("Il faut d'abord stopper YouTube (`>stop`)")
            raise Exception("Youtube playing")
