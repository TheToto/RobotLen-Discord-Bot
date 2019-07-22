import os
from dotenv import load_dotenv

load_dotenv()

# Discord
DISCORD_KEY = os.environ.get('DISCORD_KEY')
COMMAND_PREFIX = '>'

# Heroku
WEB_PORT = os.environ.get('PORT', 5000)

# API
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
KEY_GOOGLE_CONTENT = os.environ.get('KEY_GOOGLE_CONTENT')
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')

# Lavalink
LAVALINK_HOST = os.environ.get('LAVALINK_HOST')
LAVALINK_PORT = os.environ.get('LAVALINK_PORT')
LAVALINK_URI = os.environ.get('LAVALINK_URI')
LAVALINK_PASSWORD = os.environ.get('LAVALINK_PASSWORD')
