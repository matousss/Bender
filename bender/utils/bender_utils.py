import discord
import discord.ext.commands

__all__ = ['on_command_error',
           'BotMissingPermissions', 'ExtensionLoadError', 'ExtensionInitializeError']

from discord.ext.commands import Context


async def can_join_speak(ctx: discord.ext.commands.Context):
    return ctx.me.guild_permissions.speak and ctx.me.guild_permissions.connect


class BotMissingPermissions(discord.ext.commands.CommandError):
    """Raised when checking for permissions failed"""
    def __init__(self, message=None):
        super().__init__(message or 'Bot is missing permissions for that action.')

    pass


async def on_command_error(ctx: Context, error):
    """Default command error handler"""
    try:
        if isinstance(error, discord.ext.commands.CommandNotFound):
            pass
        elif isinstance(error, discord.ext.commands.errors.NotOwner):
            await ctx.send(ctx.bot.get_text("%s error_not_owner",
                                            await ctx.bot.get_language(ctx)) % ctx.author.mention)
        elif isinstance(error, discord.ext.commands.errors.CommandOnCooldown):
            await ctx.send(ctx.bot.get_text("%s on_cooldown_error",
                                            await ctx.bot.get_language(ctx)) %
                           f" ``{str(round(error.cooldown.per, 1))}s``")
        elif isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await ctx.send(ctx.bot.get_text("missing_parameters_error",
                                            await ctx.bot.get_language(ctx)))
        elif isinstance(error, discord.ext.commands.NoPrivateMessage):
            await ctx.send(ctx.bot.get_text("guild_only", await ctx.bot.get_language(ctx)))
        elif isinstance(error, discord.ext.commands.errors.BotMissingPermissions) or \
                isinstance(error, BotMissingPermissions) or isinstance(error, discord.Forbidden):
            await ctx.send(ctx.bot.get_text("bot_missing_permissions_error",
                                            await ctx.bot.get_language(ctx)))

        else:
            return True
        return False
    except discord.Forbidden:
        return False


class ExtensionInitializeError(Exception):
    """
    Raised on error, while initializing stuff from :package: `bender.modules`
    """

    def __init__(self, message: str):
        super().__init__(message)


class ExtensionLoadError(Exception):
    """
    Raised on error, while adding stuff from :package: `bender.modules`
    """

    def __init__(self, message: str):
        super().__init__(message)
