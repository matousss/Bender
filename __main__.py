import logging
import sys
import traceback
from warnings import warn

import discord
from discord.ext import commands
from discord.ext.commands import Cog

# noinspection PyUnresolvedReferences
import modules
from __init__ import __version__
from utils.config import Config
from utils.message_handler import get_text
from utils.utils import prefix as _prefix, set_global_variable, default_prefix, BenderModuleError, \
    on_command_error as oce

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
# todo descriptions

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
    print(f"<INFO> {str(command.author.name)} #{str(command.author.discriminator)} "
          f"executed command {str(command.command)}")


@BOT.event
async def on_command_error(ctx, error):
    cog = ctx.cog
    if cog and Cog._get_overridden_method(cog.cog_command_error) is not None:
        return False

    if await oce(ctx, error):
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


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
    #         logger.exception(ValueError("Token encrypting is active but required package
    #         ´cryptography.fernet´ isn't installed!"))
    #
    #
    #     if os.path.exists('/resources/token.key'):
    #         pass
    #     else:
    #         key = Fernet.generate_key()

    from utils.utils import __cogs__

    for cog in __cogs__:
        try:
            cog = cog(BOT)
        except BenderModuleError as e:
            warn(f"Cannot initialize {cog.__name__} due to error: {e}")
            continue

        try:
            BOT.add_cog(cog)
        except BenderModuleError as e:
            warn(f"Cannot load {cog.__name__} due to error: {e}")
        except Exception as e:
            traceback.print_exc()
            logger.exception(e)
    set_global_variable(__version__, 'version')
    print("Starting...")

    # if config['encrypt_token']:

    BOT.run(config['token'])
