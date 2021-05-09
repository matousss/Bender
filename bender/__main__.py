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

sys.path.append(str(pathlib.Path(__file__).parent.parent))

import bender.utils.temp as _temp
from bender.bot import Bender
# todo pydoc
from bender.utils.message_handler import MessageHandler

HELP = """
Usage: main.py [-h | -t arg]

--help | -h 
    Shows this message and ignore other arguments
--token | -t discord_token
    Override loading token from file and start app with specified token 
"""


def exit_after_enter():
    input("Press enter to continue...")
    exit(0)


def load_token(_path: os.path):
    if os.path.exists(_path):
        with open(_path, 'rt') as file:
            lines = file.readlines()

        if len(lines) > 1:
            print(f"File {_path} have invalid content. It must have one line with token!", file=sys.stderr)
            exit_after_enter()
        elif lines:
            return lines[0]
        else:
            print(f"File {_path} is empty!", file=sys.stderr)
            exit_after_enter()

    else:
        try:
            file = open(_path, 'w')
            file.close()
        except Exception:
            pass
        print("Root directory must contain file token.token with Discord token or "
              "token must be specified as argument: --token <token>", file=sys.stderr)
        exit(0)


async def start(_token: str, _bot: discord.ext.commands.Bot, is_bot: bool = True):
    try:
        await _bot.login(_token, bot=is_bot)
    except discord.LoginFailure:
        print("\033[91mLogin token is invalid")
        exit_after_enter()
        return
    except discord.HTTPException:
        print("\033[91mCannot reach Discord, please check your internet connection")
        exit_after_enter()
        return
    try:
        await _bot.connect(reconnect=True)
    except discord.PrivilegedIntentsRequired:
        print("\033[91mIntents isn't enabled! It's required to enable \"Server members intent\" at "
              "https://discord.com/developers/applications")
        exit_after_enter()
        return


def main():
    _temp.set_root_path(pathlib.Path(__file__).parent)

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
        else:
            print("Invalid arguments! Try run with --help.")
            exit(0)

    if not token:
        token = load_token(os.path.join(_temp.get_root_path(), "token.token"))

    intents = discord.Intents.default()
    intents.members = True
    print("""\n\n
       ██████╗░███████╗███╗░░██╗██████╗░███████╗██████╗░
       ██╔══██╗██╔════╝████╗░██║██╔══██╗██╔════╝██╔══██╗
       ██████╦╝█████╗░░██╔██╗██║██║░░██║█████╗░░██████╔╝
       ██╔══██╗██╔══╝░░██║╚████║██║░░██║██╔══╝░░██╔══██╗
       ██████╦╝███████╗██║░╚███║██████╔╝███████╗██║░░██║
       ╚═════╝░╚══════╝╚═╝░░╚══╝╚═════╝░╚══════╝╚═╝░░╚═╝ \n\n""")
    print("\nLoading...\n")

    message_handler = MessageHandler()
    locales_path = os.path.join(pathlib.Path(_temp.get_root_path()), "resources\\locales")
    try:
        message_handler.setup(locales_path)
    except ValueError:
        pass

    bot = Bender(message_handler=message_handler,
                 command_prefix=",", intents=intents,
                 activity=discord.Activity(type=discord.ActivityType.listening,
                                           name=f"{_temp.get_default_prefix()}help"), strip_after_prefix=True)
    if len(message_handler.get_loaded()) == 0:
        print(f"""\033[91mCouldn't load any message files.
        Please make sure, that message files are in correct directory
        e.g.:
            resources
            └── locales/
                ├── en/
                |   └── LC_MESSAGES/
                |       └── messages.po
                └── cs/
                    └── LC_MESSAGES/
                        └── messages.po  

        """)
        exit_after_enter()

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


if __name__ == "__main__":
    main()
