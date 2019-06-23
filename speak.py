import discord
from discord.ext import commands
from discord.ext.commands import Context

import youtube
from misc.googleapis import TextToSpeech
from misc.helpers import play_audio_bytes


class Speak(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def speak(self, ctx: Context, *, sentence: str):
        if ctx.voice_client is not None and ctx.voice_client.is_connected():
            audio = TextToSpeech().process(sentence)
            if ctx.voice_client.is_playing():
                ctx.voice_client.stop()
            play_audio_bytes(ctx.guild, audio)
        else:
            await ctx.send("Tu ne m'entendra pas...")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if before.channel == after.channel:
            return
        if member.bot:
            return
        guild = member.guild
        if not guild.voice_client or not guild.voice_client.is_connected() or guild.voice_client.is_playing():
            return
        voice_channel = guild.voice_client.channel
        if before.channel != voice_channel and after.channel == voice_channel:
            print(member.display_name + " join " + after.channel.name)
        if after.channel != voice_channel and before.channel == voice_channel:
            print(member.display_name + " left " + before.channel.name)

    @speak.before_invoke
    async def ensure_queue(self, ctx):
        if not ctx.guild.voice_client \
                or not ctx.guild.voice_client.is_connected():
            await ctx.send("Tu ne m'entendra pas...")
            raise Exception("Not in voice channel")
        if youtube.Queue.get(ctx.guild).is_playing():
            await ctx.send("Il faut d'abord stopper YouTube (>stop)")
            raise Exception("Youtube playing")
