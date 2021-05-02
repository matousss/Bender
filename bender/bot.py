import sys
import traceback
from warnings import warn

import discord
from discord import Guild, Forbidden, HTTPException
from discord.ext.commands import Bot, Cog, command

import bender
import bender.modules
import bender.modules.music.youtube_music

__all__ = ['Bender']


class Bender(Bot):

    async def on_ready(self):
        print("\n\n" + f'{self.user} has connected to Discord!\n\n')

        print("Connected to servers:")
        for guild in self.guilds:
            print(str(guild) + " (" + str(guild.id) + ")")

        print(f"\n\n{self.user.name} is running!\n\n")

    @staticmethod
    async def on_guild_join(guild: Guild):
        if guild.system_channel:
            try:
                await guild.system_channel.send(bender.utils.message_handler.get_text('on_join'))
            except (Forbidden, HTTPException):
                pass

    @staticmethod
    async def on_command(ctx: discord.ext.commands.Context):
        print(f"<INFO> {str(ctx.author.name)}#{str(ctx.author.discriminator)}"
              f"executed command {str(ctx.command)} in {ctx.guild}#{ctx.guild.id}")

    async def on_command_error(self, ctx, error):
        cog = ctx.cog
        if cog and Cog._get_overridden_method(cog.cog_command_error) is not None:
            return False

        if await bender.utils.bender_utils.on_command_error(ctx, error):
            print(f'Ignoring exception in command {ctx.command}:', file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    # def setup(self):
    #     from bender.utils.bender_utils import __cogs__ as cogs
    #     if len(cogs) == 0:
    #         try:
    #             cogs = default_cogs()
    #         except ImportError:
    #             raise RuntimeError("Trying to do unsupported operation or is installation corrupted?")
    #     for cog in cogs:
    #         try:
    #             cog = cog(self)
    #         except bender.utils.bender_utils.BenderModuleError as e:
    #             warn(f"Cannot initialize {cog.__name__} due to error: {e}")
    #             continue
    #
    #         try:
    #             self.add_cog(cog)
    #         except bender.utils.bender_utils.BenderModuleError as e:
    #             warn(f"Cannot load {cog.__name__} due to error: {e}")
    #         except Exception as e:
    #             print('Ignoring exception:', file=sys.stderr)
    #             traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)

    def setup(self):
        bender.utils.message_handler.setup()

        extensions = [bender.modules.info, bender.modules.moderation, bender.modules.voiceclient,
                      bender.modules.settings, bender.modules.translator, bender.modules.music.youtube_music]
        for extension in extensions:
            try:
                extension.setup(self)
            except bender.utils.bender_utils.ExtensionInitializeError as e:
                warn(f"Cannot initialize {extension.__name__} due to error: {e}")
                continue
            except bender.utils.bender_utils.ExtensionLoadError as e:
                warn(f"Cannot load {extension.__name__} due to error: {e}")
                continue
            except Exception as e:
                print('Ignoring exception:', file=sys.stderr)
                traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
                continue

        self.add_command(self.traktor)

    @staticmethod
    @command(name="traktor")
    async def traktor(ctx, *, args):
        print(ctx.message.content)

        print(args)
        print(discord.utils.escape_mentions(args))
