import discord.utils as dutils
from discord import Message
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





# from modules import __cogs__
__cogs__ = []


def bender_module(cog: Cog):

    print(f"<INFO> registered cog {cog.__name__}")
    __cogs__.append(cog)
    return cog



    return



#todo load from group settings
prefixes = {
    '-1': ',',
    '767788412446048347': 'ß'
}



def prefix(bot, message: Message) -> str:
    try:
        if message.guild:

            return prefixes[str(message.guild.id)]
    except KeyError:
        pass
    return prefixes['-1']

from .temp import global_variables

def global_variable(object, key: str = None):
    if not key:
        key = object.__name__
    global_variables[key] = object

    return global_variables[key]