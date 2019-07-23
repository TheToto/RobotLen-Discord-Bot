from discord import Activity, ActivityType, Guild, Message, utils
from discord.ext import commands

from misc import settings

import commands


def info(message: str):
    logstr = "INFO : {}".format(message)
    if settings.LOG_CHANNEL is not None:
        commands.bot.get_channel(int(settings.LOG_CHANNEL)).send(logstr)
    print(logstr)


async def log_dm(message: Message):
    if settings.DM_SECTION is None:
        return
    dm_cat = commands.bot.get_channel(int(settings.DM_SECTION))
    if dm_cat is None:
        print('DM_SECTION is wrong')
        return
    for channel in dm_cat.text_channels:
        if channel.name == str(message.author.id):
            await channel.send(message.content)
            return
    channel = await dm_cat.create_text_channel(str(message.author.id))
    await channel.send(message.author)
    await channel.send(message.content)
