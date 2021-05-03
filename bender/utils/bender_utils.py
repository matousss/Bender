import discord
import discord.ext.commands

import bender.utils.message_handler

# from discord.ext.commands import CommandNotFound, Cog, Context, CogMeta, CommandError


__all__ = ['__cogs__', 'default_prefix',
           'prefix', 'Checks', 'on_command_error',
           'BotMissingPermissions']


class Checks:
    @staticmethod
    async def can_join_speak(ctx: discord.ext.commands.Context):
        return ctx.me.guild_permissions.speak and ctx.me.guild_permissions.connect


class BotMissingPermissions(discord.ext.commands.CommandError):
    def __init__(self, message=None):
        super().__init__(message or 'Bot is missing permissions for that action.')

    pass


async def on_command_error(ctx, error):
    """Default command error handler"""
    try:
        if isinstance(error, discord.ext.commands.CommandNotFound):
            # await ctx.send(bender.utils.message_handler.get_text("command_not_found_error"))
            pass
        elif isinstance(error, discord.ext.commands.errors.NotOwner):
            await ctx.send(bender.utils.message_handler.get_text("%s error_not_owner") % ctx.author.mention)
        elif isinstance(error, discord.ext.commands.errors.CommandOnCooldown):
            # await ctx.send("Ty chceš moc věcí najednou! Počkej `" + str(int(error.cooldown.per)) + "s` saláme!")
            await ctx.send(bender.utils.message_handler.get_text("%s on_cooldown_error") %
                           f" ``{str(int(error.cooldown.per))}s``")
        elif isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await ctx.send(bender.utils.message_handler.get_text("missing_parameters_error"))
            return True
        elif isinstance(error, discord.ext.commands.NoPrivateMessage):
            await ctx.send(bender.utils.message_handler.get_text("guild_only"))
        elif isinstance(error, discord.ext.commands.errors.BotMissingPermissions) or \
                isinstance(error, BotMissingPermissions) or isinstance(error, discord.Forbidden):
            await ctx.send(bender.utils.message_handler.get_text("bot_missing_permissions_error"))

        else:
            return True
        return False
    except discord.Forbidden:
        return False


#
# def get_channel(ctx: Context, channel: str):
#     if channel.startswith("<#"):
#         return discord.utils.get(ctx.guild.channels, id=int(channel[2:].replace(">", "")))
#     elif channel.isnumeric():
#         return discord.utils.get(ctx.guild.channels, id=int(channel))
#     else:
#         return discord.utils.get(ctx.guild.channels, name=channel)


class ExtensionInitializeError(Exception):
    """
    Raised by packages in bender.modules
    """

    def __init__(self, message: str):
        super().__init__(message)


class ExtensionLoadError(Exception):
    """
    Raised by packages in bender.modules
    """

    def __init__(self, message: str):
        super().__init__(message)


# from modules import __cogs__
__cogs__ = []

# def bender_module(cog: discord.ext.commands.Cog):
#     if not isinstance(cog, (discord.ext.commands.CogMeta, discord.ext.commands.Cog)):
#         raise BenderModuleError(f"bender_module must be {discord.ext.commands.Cog.__name__} "
#                                 f"or {discord.ext.commands.CogMeta.__name__} and not "
#                                 f"{cog.__class__.__name__}")
#
#     for c in __cogs__:
#         if c.__name__ == cog.__name__:
#             break
#     else:
#         __cogs__.append(cog)
#         print(f"Registered cog {cog.__name__}")
#     return cog


# todo load from group settings
prefixes = {
    -1: ',',
    767788412446048347: ','
}


def default_prefix() -> str:
    return prefixes[-1]


# noinspection PyUnusedLocal
def prefix(bot=None, message: discord.Message = None) -> str:
    if not message:
        return prefixes[-1]
    try:
        if message.guild:
            return prefixes[message.guild.id]
    except KeyError:
        pass
    return prefixes[-1]
