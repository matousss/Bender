import logging
import sys
import traceback

import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound
from youtube_dl import DownloadError

from __init__ import __version__
# noinspection PyUnresolvedReferences
import modules
from utils.config import Config
from utils.message_handler import get_text
from utils.utils import prefix as _prefix, set_global_variable, default_prefix

# todo bender logger

# todo handle all exceptions


# todo check integrity
# todo text translations
# todo turn to app

# logger
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter("%(asctime)s %(name)-30s %(levelname)-8s %(message)s"))
logger.addHandler(handler)

intents = discord.Intents.default()
intents.members = True
BOT = commands.Bot(command_prefix=_prefix, intents=intents, owner_id=494216665664323585,
                   activity=discord.Activity(type=discord.ActivityType.listening, name=f"{default_prefix()}help"))


# todo help command


# events
@BOT.event
async def on_ready():
    print("\n\n" + f'{BOT.user} has connected to Discord!\n\n')

    print("Connected to servers:")
    for guild in BOT.guilds:
        print(str(guild) + " (" + str(guild.id) + ")")

    print(f"\n\nBender {__version__} started!")


@BOT.event
async def on_guild_join(guild):
    if guild.system_channel:
        await guild.system_channel.send(get_text('on_join'))


@BOT.event
async def on_command(command):
    print(f"<INFO> {str(command.author.name)} #{str(command.author.id)} executed command {str(command.command)}")


@BOT.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        #await ctx.send(get_text("command_not_found_error"))
        return
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
    elif isinstance(error, DownloadError):
        await ctx.send(get_text("lost_connection_error"))

    else:
        raise error


if __name__ == '__main__':
    for arg in sys.argv:
        print(arg)

    config = set_global_variable(Config(), 'config')

    # config['debug'] = True

    # todo token encryption
    #
    # if SETTINGS['encrypt_token']:
    #     try:
    #         from cryptography.fernett import Fernet
    #     except ModuleNotFoundError:
    #         logger.exception(ValueError("Token encrypting is active but required package ´cryptography.fernet´ isn't installed!"))
    #
    #
    #     if os.path.exists('/resources/token.key'):
    #         pass
    #     else:
    #         key = Fernet.generate_key()

    from utils.utils import __cogs__

    print(__cogs__)
    for cog in __cogs__:
        cog = cog(BOT)
        try:
            BOT.add_cog(cog)
        except Exception as e:
            traceback.print_exc()
            logger.exception(e)

    print("Starting...")

    # if config['encrypt_token']:

    BOT.run(config['token'])
