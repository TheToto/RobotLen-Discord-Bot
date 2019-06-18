import ctypes
import glob

import discord
from commands import launch_discord_bot

path = '/lib/x86_64-linux-gnu/'
files = [f for f in glob.glob(path + "**/*.so", recursive=True)]
for f in files:
    try:
        ctypes.cdll.LoadLibrary(f)
    except:
        print("Fail to load " + f)

discord.opus.load_opus("libopus.so")
if not discord.opus.is_loaded():
    print("Error : Can't load Opus. No voice support.")
launch_discord_bot()
