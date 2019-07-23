from discord import Activity, ActivityType, Guild, Message, utils
from discord.ext import commands

from misc import settings

import commands


def info(message: str):
    logstr = "INFO : {}".format(message)
    if settings.LOG_CHANNEL is not None:
        bot.fetch_channel(settings.LOG_CHANNEL).send(logstr)
    print(logstr)


async def log_dm(message: Message):
    if settings.DM_GUILD is None or settings.DM_SECTION is None:
        return
    dm_guild = await commands.bot.fetch_guild(settings.DM_GUILD)
    if dm_guild is None:
        print('DM_GUILD is wrong')
        return
    dm_cat = None
    for cat in dm_guild.categories:
        if cat.id == settings.DM_SECTION:
            dm_cat = cat
            break
    if dm_cat is None:
        print('DM_SECTION is wrong')
        print(dm_guild.channels)
        return
    for channel in dm_cat.text_channels:
        if channel.name == str(message.author.id):
            await channel.send(message.content)
            break
    channel = await dm_cat.create_text_channel(str(message.author.id))
    await channel.send(message.author)
    await channel.send(message.content)
