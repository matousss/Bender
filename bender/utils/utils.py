import discord.utils as dutils
from discord.ext.commands import Context

from ..modules import __cogs__

__all__ = ['BenderModuleError', 'BenderModule']


def get_channel(ctx: Context, channel: str):
    if channel.startswith("<#"):
        return dutils.get(ctx.guild.channels, id=int(channel[2:].replace(">", "")))
    elif channel.isnumeric():
        return dutils.get(ctx.guild.channels, id=int(channel))
    else:
        return dutils.get(ctx.guild.channels, name=channel)


class BenderModuleError(Exception):
    """
    Raised by packages in bender.modules
    """

    def __init__(self, message: str):
        super().__init__(message)


class BenderModule(object):
    def __init__(self, cog=None):
        for c in __cogs__:
            if cog.__name__ == c.__name__:
                return
        __cogs__.append(cog)
    pass
