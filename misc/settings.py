import os
from dotenv import load_dotenv

load_dotenv()

# Discord
DISCORD_KEY = os.environ['DISCORD_KEY']
COMMAND_PREFIX = '>'

# Heroku
WEB_PORT = os.environ['PORT']
