import discord

from commands import launch_discord_bot

if not discord.opus.is_loaded():
    discord.opus.load_opus('libopus.so')

launch_discord_bot()
