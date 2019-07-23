import os
from dotenv import load_dotenv

load_dotenv()

# Discord
DISCORD_KEY = os.environ.get('DISCORD_KEY')  # Discord API KEY
COMMAND_PREFIX = '>'

LOG_CHANNEL = os.environ.get('DISCORD_LOG_CHANNEL', None)  # The discord channel to send logs (optional)
DM_SECTION = os.environ.get('DISCORD_DM_SECTION', None)  # The section to place DMs (optional)

TRUSTED_USERS = os.environ.get('DISCORD_TRUSTED_USERS', '').split(',')  # List of trusted users for advanced commands
INSULTS = os.environ.get('INSULTS', '').split(',')

# APIs
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')  # For Text to speech (key.json)
KEY_GOOGLE_CONTENT = os.environ.get('KEY_GOOGLE_CONTENT')
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')  # For sub command (show yt channel infos)

# Lavalink (For music cog)
LAVALINK_HOST = os.environ.get('LAVALINK_HOST')
LAVALINK_PORT = os.environ.get('LAVALINK_PORT')
LAVALINK_URI = os.environ.get('LAVALINK_URI')
LAVALINK_PASSWORD = os.environ.get('LAVALINK_PASSWORD')
