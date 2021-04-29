from discord.ext.commands import Cog, command, Context, Bot, cooldown

__all__ = ['Info']

from utils.message_handler import get_text
from utils.utils import bender_module, get_global_variable


@bender_module
class Info(Cog):
    def __init__(self, bot: Bot):
        self.BOT: Bot = bot
        print(f"Initialized {str(__name__)}")

    @command(name="info")
    @cooldown(1, 10)
    async def _info(self, ctx):
        await ctx.send(get_text("%s info") % get_global_variable('version'))
        pass

    @command(name="ping")
    async def ping(self, ctx: Context):
        # print("<INFO> ping: "+str(float(bot.latency)*1000).split(".")[0] +"ms")
        await ctx.send(f"{get_text('ping')}: ``{str(round(float(ctx.bot.latency) * 1000))}ms``")

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
    pass

