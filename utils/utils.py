import subprocess

import discord.ext
import discord.utils as dutils
from discord import Message

__all__ = ['get_channel', 'BenderModuleError', '__cogs__', 'bender_module', 'default_prefix',
           'prefix', 'set_global_variable', 'get_global_variable', 'Checks']

from discord.ext.commands import CommandNotFound, Cog, Context, CogMeta

from .message_handler import get_text


class Checks:
    @staticmethod
    async def can_join_speak(ctx: Context):
        return ctx.me.guild_permissions.speak and ctx.me.guild_permissions.connect

    @staticmethod
    def checkFFMPEG() -> bool:
        """
        Check for ffmpeg/avconv
        """
        try:
            subprocess.check_call(['ffmpeg', '-version'],
                                  stdout=subprocess.DEVNULL,
                                  stderr=subprocess.STDOUT)
        except Exception:
            try:
                subprocess.check_call(['avconv', '-version'],
                                      stdout=subprocess.DEVNULL,
                                      stderr=subprocess.STDOUT)
            except Exception:
                return False
        return True


async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        # await ctx.send(get_text("command_not_found_error"))
        pass
    elif isinstance(error, discord.ext.commands.errors.NotOwner):
        await ctx.send(get_text("%s error_not_owner") % ctx.author.mention)
    elif isinstance(error, discord.ext.commands.errors.CommandOnCooldown):
        # await ctx.send("Ty chceš moc věcí najednou! Počkej `" + str(int(error.cooldown.per)) + "s` saláme!")
        await ctx.send(get_text("%s on_cooldown_error") % f" ``{str(int(error.cooldown.per))}s``")
    elif isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.send(get_text("missing_parameters_error"))
    elif isinstance(error, discord.ext.commands.NoPrivateMessage):
        await ctx.send(get_text("guild_only"))
    elif isinstance(error, discord.ext.commands.errors.BotMissingPermissions):
        await ctx.send(get_text("missing_permissions"))

    else:
        return True
    return False

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
    if not isinstance(cog, (CogMeta, Cog)):
        raise BenderModuleError(f"bender_module must be {Cog.__name__} or {CogMeta.__name__} and not "
                                f"{cog.__class__.__name__}")

    print(f"<INFO> registered cog {cog.__name__}")
    __cogs__.append(cog)
    return cog

    return


# todo load from group settings
prefixes = {
    '-1': ',',
    '767788412446048347': 'ß'
}


def default_prefix() -> str:
    return prefixes['-1']


def prefix(bot, message: Message) -> str:
    try:
        if message.guild:
            return prefixes[str(message.guild.id)]
    except KeyError:
        pass
    return prefixes['-1']


from .temp import global_variables


def set_global_variable(object, key=None):
    if not key:
        key = object.__name__
    global_variables[key] = object

    return global_variables[key]


def get_global_variable(key):
    try:
        return global_variables[key]
    except:
        raise
