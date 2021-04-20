import discord.utils as dutils
from discord.ext.commands import Context, Cog

__all__ = ['BenderModuleError', 'bender_module']


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


from bender.modules import __cogs__


def bender_module(cog: Cog):
    for c in __cogs__:
        if cog.__name__ == c.__name__:
            return
    print(f"<INFO> registered cog {cog.__name__}")
    __cogs__.append(cog)

    pass
