from asyncio import get_event_loop

from discord.ext.commands import Cog, command, is_owner

__all__ = ['Info']

from bender.utils.utils import BenderModule


@BenderModule
class Info(Cog):
    def __init__(self, bot):
        self.bot = bot
        print(f"Initialized {str(__name__)}")

    # @commands.command(name="info")
    # async def _info(self, ctx):
    #     await MessagesHandler.sendMessage(self,ctx, MessagesTexts.info)
    #     pass

    @command(name="ping")
    async def _ping(self, ctx):
        # print("<INFO> ping: "+str(float(bot.latency)*1000).split(".")[0] +"ms")
        await ctx.send(f"Ping: `{str(round(float(ctx.BOT.latency) * 1000))}ms`")

    @command(name="suicide")
    @is_owner()
    async def _suicide(self, ctx):
        get_event_loop().stop()
        pass

    @command(name="deleteme", aliases=['dem'])
    async def _deleteme(self, ctx, args):
        await ctx.message.delete()
    pass
