# import logging
# import sys
# import traceback
# from warnings import warn
#
# import discord
# from discord.ext import commands
# from discord.ext.commands import Cog
#
# # noinspection PyUnresolvedReferences
# import bender.modules
# from bender import __version__
# from bender.utils.config import Config
# from bender.utils.message_handler import get_text
# from bender.utils.utils import prefix as _prefix, set_global_variable, default_prefix, BenderModuleError, \
#     on_command_error as oce
#
#
#

#
# # logger
# logger = logging.getLogger('discord')
# logger.setLevel(logging.DEBUG)
# handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
# handler.setFormatter(logging.Formatter("%(asctime)s %(name)-30s %(levelname)-8s %(message)s"))
# logger.addHandler(handler)
#
# intents = discord.Intents.default()
# intents.members = True
# BOT = commands.Bot(command_prefix=_prefix, intents=intents,
#                    activity=discord.Activity(type=discord.ActivityType.listening, name=f"{default_prefix()}help"))
#
#
#
#
# # events
# @BOT.event
# async def on_ready():
#     print("\n\n" + f'{BOT.user} has connected to Discord!\n\n')
#
#     print("Connected to servers:")
#     for guild in BOT.guilds:
#         print(str(guild) + " (" + str(guild.id) + ")")
#
#     print(f"\n\nBender {__version__} started!")
#
#
# @BOT.event
# async def on_guild_join(guild):
#     if guild.system_channel:
#         await guild.system_channel.send(get_text('on_join'))
#
#
# @BOT.event
# async def on_command(command):
#     print(f"<INFO> {str(command.author.name)} #{str(command.author.discriminator)} "
#           f"executed command {str(command.command)}")
#
#
# @BOT.event
# async def on_command_error(ctx, error):
#     cog = ctx.cog
#     if cog and Cog._get_overridden_method(cog.cog_command_error) is not None:
#         return False
#
#     if await oce(ctx, error):
#         print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
#         traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
#
#
# if __name__ == '__main__':
#     for arg in sys.argv:
#         print(arg)
#
#     config = set_global_variable(Config(), 'config')
#
#
#
#     from bender.utils.utils import __cogs__
#
#     for cog in __cogs__:
#         try:
#             cog = cog(BOT)
#         except BenderModuleError as e:
#             warn(f"Cannot initialize {cog.__name__} due to error: {e}")
#             continue
#
#         try:
#             BOT.add_cog(cog)
#         except BenderModuleError as e:
#             warn(f"Cannot load {cog.__name__} due to error: {e}")
#         except Exception as e:
#             traceback.print_exc()
#             logger.exception(e)
#     set_global_variable(__version__, 'version')
#
#     print("Starting...")
#
#     # if config['encrypt_token']:
#
#     BOT.run(config['token'])
import asyncio
import os
import pathlib
import sys

import discord
import discord.ext.commands

import bender
from bender.bot import Bender
from bender.utils import bender_utils
from bender.utils.config import Config

# todo config
# todo settings
# todo texts
# todo pydoc
HELP = """
Usage: main.py [-h | -t arg]

--help | -h 
    Shows this message and ignore other arguments
--token | -t discord_token
    Override loading token from file and start app with specified token 
"""


def load_token(_path: os.path):
    if os.path.exists(_path):
        with open(_path, 'rt') as file:
            lines = file.readlines()

        if len(lines) > 1:
            print(f"File {_path} have invalid content. It must have one line with token!", file=sys.stderr)
            exit(0)
        else:
            return lines[0]

    else:
        print("Root directory must contain file token.token with Discord token or "
              "token must be specified as argument: --token <token>", file=sys.stderr)
        exit(0)


async def start(_token: str, _bot: discord.ext.commands.Bot, is_bot: bool = True):
    try:
        await _bot.login(_token, bot=is_bot)
    except discord.LoginFailure:
        print("Login token is invalid", file=sys.stderr)
        input("Press enter to continue...")
        return
    except discord.HTTPException:
        print("Cannot reach Discord, please check your internet connection", file=sys.stderr)
        input("Press enter to continue...")
        return
    await _bot.connect(reconnect=True)


if __name__ == "__main__":
    token = None
    if len(sys.argv) > 1:
        if len(sys.argv) > 3:
            print("Too much arguments! Try run with --help.")
            exit(0)

        if sys.argv[1] in ("--help", "-h"):
            print(HELP)
            exit(0)
        elif sys.argv[1] in ("--token", "-t"):
            token = sys.argv[2]

    path = pathlib.Path(__file__).parent.joinpath("./token.token")
    token = load_token(path)

    if not token:
        config = Config()
        config = bender_utils.set_global_variable(config, 'config')

    intents = discord.Intents.default()
    intents.members = True
    print("""\n\n
       ██████╗░███████╗███╗░░██╗██████╗░███████╗██████╗░
       ██╔══██╗██╔════╝████╗░██║██╔══██╗██╔════╝██╔══██╗
       ██████╦╝█████╗░░██╔██╗██║██║░░██║█████╗░░██████╔╝
       ██╔══██╗██╔══╝░░██║╚████║██║░░██║██╔══╝░░██╔══██╗
       ██████╦╝███████╗██║░╚███║██████╔╝███████╗██║░░██║
       ╚═════╝░╚══════╝╚═╝░░╚══╝╚═════╝░╚══════╝╚═╝░░╚═╝ v%s\n\n""" % bender.__version__)
    print("\nLoading...\n")
    bot = Bender(command_prefix=bender_utils.prefix, intents=intents,
                 activity=discord.Activity(type=discord.ActivityType.listening,
                                           name=f"{bender_utils.default_prefix()}help"))
    bot.setup()
    print("\nStarting...\n")

    loop = asyncio.get_event_loop()
    task = start(token, bot)
    try:
        loop.run_until_complete(task)
    except KeyboardInterrupt:
        loop.run_until_complete(bot.close())
    finally:
        if loop.is_running():
            loop.close()
