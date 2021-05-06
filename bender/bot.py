import importlib
import sys
import traceback
from datetime import datetime
from warnings import warn

import discord
from discord import Guild, Forbidden, HTTPException
from discord.ext.commands import Bot, Cog, Context, NoPrivateMessage

import bender.utils.bender_utils
from bender.utils import temp as _temp
from bender.utils.message_handler import MessageHandler

__all__ = ['Bender', 'BenderCog']


def guild_only(ctx):
    if not ctx.guild:
        raise NoPrivateMessage("Command can be used only in guild")
    return True


class Bender(Bot):
    def __init__(self, *args, message_handler: MessageHandler, **kwargs, ):
        self._message_handler = message_handler
        self.loaded_languages = None
        self.get_text = None
        super().__init__(*args, **kwargs)
        self.add_check(guild_only)

    async def on_ready(self):

        print("\n\n" + f'{self.user} has connected to Discord!\n\n')

        print("Connected to servers:")
        for guild in self.guilds:
            print(str(guild) + " (" + str(guild.id) + ")")

        print(f"\n\n{self.user.name} is running!\n\n")

    async def on_guild_join(self, guild: Guild) -> None:
        if guild.system_channel:
            try:
                await guild.system_channel.send(self.get_text('on_join', _temp.get_default_language()))
            except (Forbidden, HTTPException):
                pass
        print(f"<INFO> [{datetime.now().strftime('%H:%M:%S')}] Joined guild {guild.name}")

    async def on_guild_remove(self, guild: Guild) -> None:
        print(f"<INFO> [{datetime.now().strftime('%H:%M:%S')}] Left guild {guild.name}")

    async def on_command(self, ctx: discord.ext.commands.Context):
        print(f"<INFO> [{datetime.now().strftime('%H:%M:%S')}] {str(ctx.author.name)}#{str(ctx.author.discriminator)}"
              f"executed command {str(ctx.command)} {(f'in {ctx.guild}#{ctx.guild.id}' if ctx.guild else '')}")

    async def on_command_error(self, ctx, error):
        cog = ctx.cog
        if cog and Cog._get_overridden_method(cog.cog_command_error) is not None:
            return

        if await bender.utils.bender_utils.on_command_error(ctx, error):
            print(f'Ignoring exception in command {ctx.command}:', file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    async def get_language(self, ctx: Context):
        return _temp.get_default_language()

    def setup(self):
        self.loaded_languages = tuple(self._message_handler.locales.keys())
        self.get_text = self._message_handler.get_text
        extensions = ["bender.modules.info", "bender.modules.moderation", "bender.modules.settings",
                      "bender.modules.voiceclient", "bender.modules.music.youtube_music"]
        for extension in extensions:
            try:
                imported = importlib.import_module(extension)
                imported.setup(self)
            except bender.utils.bender_utils.ExtensionInitializeError as e:
                warn(f"Cannot initialize {extension} due to error: {e}")
                continue
            except bender.utils.bender_utils.ExtensionLoadError as e:
                warn(f"Cannot load {extension} due to error: {e}")
                continue
            except Exception as e:
                print('Ignoring exception:', file=sys.stderr)
                traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
                continue


class BenderCog(Cog):
    def __init__(self, bot: Bender) -> None:
        self.bot = bot
        self.get_text = self.bot.get_text
        self.get_language = self.bot.get_language
        super().__init__()
        print(f"Initialized {str(self.__class__.__name__)}")

    pass
