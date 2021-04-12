from asyncio.queues import Queue

import discord.utils as dutils

__all__=['']




def get_channel(ctx, channel: str):
    if channel.startswith("<#"):
        return dutils.get(ctx.guild.channels, id=int(channel[2:].replace(">", "")))
    elif channel.isnumeric():
        return dutils.get(ctx.guild.channels, id=int(channel))
    else:
        return dutils.get(ctx.guild.channels, name=channel)


