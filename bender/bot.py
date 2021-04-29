import sys
import traceback
from warnings import warn

from discord.ext.commands import Bot, Cog

from bender import __version__
from bender.utils.message_handler import get_text
from bender.utils.utils import on_command_error as oce, BenderModuleError


class Bender(Bot):
    async def on_ready(self):
        print("\n\n" + f'{self.user} has connected to Discord!\n\n')

        print("Connected to servers:")
        for guild in self.guilds:
            print(str(guild) + " (" + str(guild.id) + ")")

        print(f"\n\nBender {__version__} started!")

    async def on_guild_join(self, guild):
        if guild.system_channel:
            await guild.system_channel.send(get_text('on_join'))

    async def on_command(self, command):
        print(f"<INFO> {str(command.author.name)} #{str(command.author.discriminator)} "
              f"executed command {str(command.command)}")

    async def on_command_error(self, ctx, error):
        cog = ctx.cog
        if cog and Cog._get_overridden_method(cog.cog_command_error) is not None:
            return False

        if await oce(ctx, error):
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    def setup(self):

        from bender.utils.utils import __cogs__
        for cog in __cogs__:
            try:
                cog = cog(self)
            except BenderModuleError as e:
                warn(f"Cannot initialize {cog.__name__} due to error: {e}")
                continue

            try:
                self.add_cog(cog)
            except BenderModuleError as e:
                warn(f"Cannot load {cog.__name__} due to error: {e}")
            except Exception as e:
                print('Ignoring exception:', file=sys.stderr)
                traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
