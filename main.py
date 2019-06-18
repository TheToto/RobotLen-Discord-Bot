import threading

from misc import web_server
from commands import launch_discord_bot

# For Heroku free dynos
threading.Thread(target=web_server.launch_web_server).start()
launch_discord_bot()
