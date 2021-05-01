import sys
import traceback
from warnings import warn

import discord
from discord import Member, Role
from discord.ext.commands import Bot, Cog, command, Greedy

import bender

__all__ = ['Bender']


def default_cogs():
    from bender.modules import info
    from bender.modules import moderation
    from bender.modules import translator
    from bender.modules import voiceclient
    from bender.modules.music import youtube_music

    return [info.Info, moderation.Moderation, translator.GoogleTranslator, voiceclient.VoiceClientCommands,
            youtube_music.YoutubeMusic]

class Bender(Bot):
    async def on_ready(self):
        print("\n\n" + f'{self.user} has connected to Discord!\n\n')

        print("Connected to servers:")
        for guild in self.guilds:
            print(str(guild) + " (" + str(guild.id) + ")")

        print(f"\n\nBender {bender.__version__} started!")

    @staticmethod
    async def on_guild_join(guild):
        if guild.system_channel:
            await guild.system_channel.send(bender.utils.message_handler.get_text('on_join'))

    @staticmethod
    async def on_command(cmd):
        print(f"<INFO> {str(cmd.author.name)} #{str(cmd.author.discriminator)} "
              f"executed command {str(cmd.command)}")

    async def on_command_error(self, ctx, error):
        cog = ctx.cog
        if cog and Cog._get_overridden_method(cog.cog_command_error) is not None:
            return False

        if await bender.utils.bender_utils.on_command_error(ctx, error):
            print(f'Ignoring exception in command {ctx.command}:', file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    def setup(self):
        from bender.utils.bender_utils import __cogs__ as cogs
        if len(cogs) == 0:
            try:
                cogs = default_cogs()
            except ImportError:
                raise RuntimeError("Trying to do unsupported operation or installation is corrupted")
        for cog in cogs:
            try:
                cog = cog(self)
            except bender.utils.bender_utils.BenderModuleError as e:
                warn(f"Cannot initialize {cog.__name__} due to error: {e}")
                continue

            try:
                self.add_cog(cog)
            except bender.utils.bender_utils.BenderModuleError as e:
                warn(f"Cannot load {cog.__name__} due to error: {e}")
            except Exception as e:
                print('Ignoring exception:', file=sys.stderr)
                traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)



        self.add_command(self.traktor)

    @staticmethod
    @command(name="traktor")
    async def traktor(ctx, *, args):
        print(ctx.message.content)

        print(args)
        print(discord.utils.escape_mentions(args))
