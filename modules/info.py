from typing import Optional

from discord import Embed
from discord.ext.commands import Cog, command, Context, Bot, cooldown

__all__ = ['Info']

from utils.message_handler import get_text
from utils.utils import bender_module, get_global_variable


@bender_module
class Info(Cog):
    def __init__(self, bot: Bot):
        self.BOT: Bot = bot
        bot.remove_command('help')
        print(f"Initialized {str(__name__)}")

    @command(name="info", description=get_text("command_info_description"),
             help=get_text("command_info_help"))
    @cooldown(1, 10)
    async def _info(self, ctx):
        await ctx.send(get_text("%s info") % get_global_variable('version'))
        pass

    @command(name="ping", description=get_text("command_ping_description"),
             help=get_text("command_ping_help"))
    @cooldown(1, 10)
    async def ping(self, ctx: Context):
        # print("<INFO> ping: "+str(float(bot.latency)*1000).split(".")[0] +"ms")
        await ctx.send(get_text('%s ping') % f"``{str(round(float(ctx.bot.latency) * 1000))}ms``")

    # @command(name="suicide")
    # @is_owner()
    # async def suicide(self, ctx):
    #     get_event_loop().stop()
    #     pass
    #
    # @command(name="deleteme", aliases=['dem'])
    # @guild_only()
    # async def deleteme(self, ctx, args):
    #     await ctx.message.delete()
    #     await ctx.send(get_text("%s smazal zprávu") % ctx.author.mention)

    @command(name="help", description=get_text("command_help_description"),
             help=get_text("command_help_help"))
    @cooldown(1, .5)
    async def help(self, *, args: Optional[str] = None):
        if not args:
            embed = Embed(color=0xff0000)

    pass
