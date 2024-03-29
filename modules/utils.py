import sys
import typing
from .messages import MessagesHandler
from .messages import MessagesTexts
from discord.ext import commands
from googletrans import Translator
from discord import utils as dutils


class BenderUtils():
    def getChannel(self, ctx, channel: str):
        if channel.startswith("<#"):
            return dutils.get(ctx.guild.channels, id=int(channel[2:].replace(">", "")))
        elif channel.isnumeric():
            return dutils.get(ctx.guild.channels, id=int(channel))
        else:
            return dutils.get(ctx.guild.channels, name=channel)

    pass
butils = BenderUtils()

class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("Initialized modules.utils.Utils")

    @commands.command(name="info")
    async def _info(self, ctx):
        await MessagesHandler.sendMessage(self,ctx, MessagesTexts.info)
        pass

    @commands.command(name="ping")
    async def ping(self, ctx):
        # print("<INFO> ping: "+str(float(bot.latency)*1000).split(".")[0] +"ms")
        await ctx.send("Ping: `" + str(float(self.ctx.bot.latency) * 1000).split(".")[0] + "ms`")

    @commands.command(name="suicide")
    @commands.is_owner()
    async def _suicide(self, ctx):
        sys.exit("Killed by Owner!")
        pass

    pass


def have_match(input, what):
    if input is None:
        return True
    for i in input:

        if int(i) == what:
            return True
    return False


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("Initialized modules.utils.Moderation")
        pass

    # @commands.command(name="moveall", aliases=["mall"])
    # async def _moveall(ctx, *channel: str):
    #     channel = str(" ".join(channel))
    #     destination = None
    #
    #     if channel == "":
    #         await ctx.send(messages.moveall_error)
    #         return
    #     if channel and channel is not None:
    #         if channel.startswith("<"):
    #             destination = discord.utils.get(ctx.guild.channels, id=int(channel[2:].replace(">", "")))
    #         elif channel.isnumeric():
    #             destination = discord.utils.get(ctx.guild.channels, id=int(channel))
    #
    #         else:
    #             destination = discord.utils.get(ctx.guild.channels, name=channel)
    #         if destination is None:
    #             await ctx.send(messages.moveall_error_b + " `" + channel + "`")
    #             return
    #
    #
    #     elif False:
    #         print("1")
    #         if ctx.author.voice and ctx.author.voice.channel:
    #             print("3")
    #             author = discord.utils.get(ctx.guild.members, name=str(ctx.author))
    #             await ctx.send("Join channel and take everyone from current channel with you!")
    #             try:
    #                 print("4")
    #                 async with timeout(20):
    #                     print("5")
    #                     while True:
    #                         print("5")
    #                         print(author.voice.channel.id)
    #                         print(ctx.author.voice.channel.id)
    #                         if ctx.author.voice.channel.id != author.voice.channel.id:
    #                             destination = ctx.author.voice.channel
    #                             print("0")
    #
    #             except asyncio.TimeoutError:
    #                 await ctx.send("Time out!")
    #                 return
    #         else:
    #             await ctx.send("User isn't in channel or no channel specified!")
    #             return
    #
    #     for mem in ctx.author.voice.channel.members:
    #
    #         if mem != ctx.author:
    #             await ctx.author.move_to(destination)
    #             await mem.move_to(destination)
    #             print("<INFO> Moved user: " + str(mem) + " to " + str(destination))
    #     await ctx.author.move_to(destination)
    #     print("<INFO> Moved user: " + str(ctx.author) + " to " + str(destination))
    #     await ctx.send(messages.moveall + " `" + str(destination) + "`")
    #     pass

    # @commands.command(name="kickothers", aliases=["kothers"])
    # async def _kickothers(ctx):
    #     if ctx.author.voice and ctx.author.voice.channel:
    #         if len(ctx.author.voice.channel.members == 1):
    #             ctx.send(messages.kothers_error)
    #             return
    #         for mem in ctx.author.voice.channel.members:
    #             if mem != ctx.author:
    #                 await ctx.author.move_to(None)
    #                 await mem.move_to(None)
    #                 print("<INFO> Kicked user: " + str(mem) + " from " + str(ctx.author.voice.channel))
    #     else:
    #         await ctx.send(messages.kick_error)
    #     await ctx.send(messages.kothers)
    #     pass

    # @commands.command(name="kickall", aliases=["kall"])
    # async def _kickall(ctx):
    #     channel = ctx.author.voice.channel
    #     if ctx.author.voice and ctx.author.voice.channel:
    #         for mem in ctx.author.voice.channel.members:
    #             if mem != ctx.author:
    #                 await ctx.author.move_to(None)
    #                 await mem.move_to(None)
    #                 print("<INFO> Kicked user: " + str(mem) + " from " + str(ctx.author.voice.channel))
    #     else:
    #         await ctx.send(messages.kick_error)
    #     await ctx.author.move_to(None)
    #     print("<INFO> Kicked user: " + str(ctx.author) + " from " + str(channel))
    #     await ctx.send(messages.kall + " `" + str(ctx.author.voice.channel) + "`")
    #     pass

    @commands.command(name="kick", aliases=["k"])
    async def _kick(self, ctx, option: str = None, channel: typing.Optional[str] = None, *,
                    users: typing.Optional[str] = ""):
        destination = None
        if option and option.startswith("<@"):
            users += option
            option = "all"

        if channel and channel.startswith("<@"):
            users += channel
            channel = None
        if channel is None and option != "all" and option != "others" and option != "a" and option != "o" and option is not None:
            channel = option
            option = "all"
        if option is None:
            await ctx.send("Syntax error")
            return
        if channel is not None:
            destination = butils.getChannel(ctx ,channel)

        if ctx.author.voice and ctx.author.voice.channel and channel is None:
            destination = ctx.author.voice.channel
        elif destination is None:
            await ctx.send("No possible voice channel found!")
            return
        usersIdList = None

        if users != "":
            users = users.replace(",", "").replace("<@!", " ").replace(">", "").replace("\n", "")
            users = " ".join(users.split())
            usersIdList = users.split(" ")
            force_all = False
        else:
            force_all = True
        if option == "all" or option == "a":
            a = True
        elif option == "others" or option == "o":
            a = False
            if usersIdList is None:
                usersIdList = [ctx.author.id]
        else:
            print("<ERROR> An error occured while executing _kick")

        for mem in destination.members:

            if have_match(usersIdList, mem.id) == a or force_all is True:
                await mem.move_to(None)
                print("<INFO> Kicked user: " + str(mem) + " from " + str(destination))

        pass

    @commands.command(name="move", aliases=["m", "mv"])
    async def _move(self, ctx, option: str = None, arg_source: typing.Optional[str] = "",
                    arg_destination: typing.Optional[str] = "", *, users: typing.Optional[str] = ""):
        get_destination = None
        get_source = None
        if option == "all" or option == "a" or option == "o" or option == "others":
            if arg_source.startswith("<@") or arg_source == "":
                await ctx.send("Syntax error!")
                return
            if arg_destination.startswith("<@") or arg_destination == "":
                if ctx.author.voice and ctx.author.voice.channel:
                    get_destination = arg_source
                    source = ctx.author.voice.channel
                    if arg_destination.startswith("<@"):
                        users += arg_destination
                else:
                    await ctx.send("None source channel defined!2")
                    return
            else:
                get_source = arg_source
                get_destination = arg_destination
            if option == "all" or option == "a":
                a = True
            elif option == "others" or option == "o":
                a = False
        else:
            a = True
            if arg_source is None or arg_source.startswith("<@"):
                if ctx.author.voice and ctx.author.voice.channel:
                    get_destination = option
                    source = ctx.author.voice.channel
                else:
                    await ctx.send("None source channel defined!")
                    return
                if arg_source.startswith("<@"):
                    users += arg_source
                    users += arg_destination
            else:
                get_source = option
                get_destination = arg_source
                users += arg_destination

        if get_destination is not None:
            destination = butils.getChannel(ctx, get_destination)

        if get_source is not None:
            source = butils.getChannel(ctx, get_source)
        if source is None or destination is None:
            await ctx.send("Wrong channel!")
            return
        usersIdList = None
        force_all = False
        if users != "":
            users = users.replace(",", "").replace("<@!", " ").replace(">", "").replace("\n", "")
            users = " ".join(users.split())
            usersIdList = users.split(" ")
        else:
            force_all = True

        for mem in source.members:

            if force_all is True or have_match(usersIdList, mem.id) == a:
                await mem.move_to(destination)
                print("<INFO> Moved user: " + str(mem) + " to " + str(destination))

        pass

    pass


class GoogleTranslator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("Initalized modules.utils.GoogleTranslator")

    @commands.command(name="translate", aliases=["tr"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def _translate(self, ctx, lang: str, seclang: typing.Optional[str] = "", *,
                         content: typing.Optional[str] = ""):
        traslator = Translator()
        destlang = "cs"  # Settings.language
        srclang = None
        if lang.startswith("("):
            if lang.endswith(")"):
                destlang = lang.replace("(", "").replace(")", "")
            else:
                await ctx.send("Syntax error!")
                return
            if seclang.startswith("("):
                if seclang.endswith(")"):
                    srclang = seclang.replace("(", "").replace(")", "")
                else:
                    await ctx.send("Syntax error")
            else:
                content = seclang + " " + content
        else:
            content = lang + " " + seclang + " " + content

        try:
            if srclang is None:
                product = traslator.translate(content, dest=destlang)

            else:
                product = traslator.translate(content, src=srclang, dest=destlang)
        except ValueError:
            await ctx.send("Invalid language code!")
            return
        await ctx.send("Translated from `" + product.src + "` as `" + product.text + "`")


class Greetings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send('Welcome {0.mention}.'.format(member))

    @commands.command()
    async def hello(self, ctx, *, member: str = None):
        """Says hello"""
        member = member or ctx.author
        if self._last_member is None or self._last_member.id != member.id:
            await ctx.send('Hello {0.name}~'.format(member))
        else:
            await ctx.send('Hello {0.name}... This feels familiar.'.format(member))
        self._last_member = member

    pass
