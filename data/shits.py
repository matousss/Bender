from threading import Thread

from discord import utils
from discord.ext import commands


class Shits(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("Initialized modules.shits.Shits")

    running = True

    @commands.command(name="loopkick")
    @commands.is_owner()
    async def _loopkick(self, ctx, *, id: str):
        running = True
        if id.startswith("<@"):
            id = id.replace("<@!", "")
            id = id.replace(">", "")
        target = utils.get(ctx.guild.members, id=int(id))

        async def loop():
            while running is True:
                await target.edit(voice_channel=None)

        Thread(target=await loop())

    @commands.command(name="loopmute")
    @commands.is_owner()
    async def _loopkick(self, ctx, *, id: str):
        running = True
        if id.startswith("<@"):
            id = id.replace("<@!", "")
            id = id.replace(">", "")
        target = utils.get(ctx.guild.members, id=int(id))

        async def loop():
            while running is True:
                await target.edit(mute=True)

        Thread(target=await loop())
        pass

    @commands.command(name="stopallloops", aliases=["sal"])
    async def _stopallloops(self, ctx):
        running = False
        pass

    @commands.command(name="test2")
    async def _test2(self, ctx):
        if ctx.author.voice and ctx.author.voice.channel:
            for mem in ctx.author.voice.channel.members:
                if mem != ctx.author:
                    print("<TEST> User: " + str(mem))
            await ctx.send("Success!")
        else:
            await ctx.send("test2")
        pass

    @commands.command(name="test", aliases=["t"])
    async def _test(self, ctx, *str: str):
        test = " ".join(str)
        if test == "":
            await ctx.send("test")
            return
        await ctx.send(test, tts=True)
        pass

