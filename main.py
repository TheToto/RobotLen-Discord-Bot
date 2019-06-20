import discord
from misc import settings

from commands import launch_discord_bot

if not discord.opus.is_loaded():
    discord.opus.load_opus('libopus.so')

file = open(settings.GOOGLE_APPLICATION_CREDENTIALS, 'w')
file.write(settings.KEY_GOOGLE_CONTENT)
file.close()

launch_discord_bot()
