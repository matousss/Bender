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
# # todo handle all exceptions
#
#
#
# # todo text translations
# # todo turn to app
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
#     # todo token encryption
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
import sys

from discord import Activity, ActivityType, Intents

from bender import modules
from bender.utils import bender_utils
from bender.utils.config import Config
from bender.bot import Bender

if __name__ == "__main__":
    for arg in sys.argv[1:]:
        print(arg)
    config = Config()
    config = bender_utils.set_global_variable(config, 'config')

    # todo token encryption
    intents = Intents.default()
    intents.members = True
    print("Loading...")
    bot = Bender(command_prefix=bender_utils.prefix, intents=intents,
                 activity=Activity(type=ActivityType.listening, name=f"{bender_utils.default_prefix()}help"))
    bot.setup()
    print("Starting...")

    bot.run(config['token'])
