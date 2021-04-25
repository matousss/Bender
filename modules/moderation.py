import typing

from discord.ext.commands import Cog, command, Context, group


from utils import utils as butils

__all__ = ['Moderation']

from utils.utils import bender_module
from utils.message_handler import get_text


@bender_module
class Moderation(Cog):


    def __init__(self, bot):
        self.bot = bot
        print(f"Initialized {str(__name__)}")




    @staticmethod
    def have_match(input_list, what):
        if input_list is None:
            return True
        for i in input_list:
            if int(i) == what:
                return True
        return False

    @group(name="kick", aliases=["k"])
    async def kick(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            print(ctx.message.mentions)
            await ctx.invoke(self.all)
        pass


    #todo https://discordpy.readthedocs.io/en/latest/ext/commands/commands.html#greedy
    @kick.command(aliases=['a'])
    async def all(self, ctx: Context, *, destination: typing.Optional[str] = None):
        if destination:
            if '<@' in destination:
                destination = destination.split('<@', 1)[0]
            destination = butils.get_channel(ctx, destination.lstrip())
        else:
            if ctx.author.voice and ctx.author.voice.channel:
                destination = ctx.author.voice.channel

        if not destination:
            await ctx.send((get_text("no_channel_error")), reference=ctx.message, mention_author=False)

        return

        kicked = 0
        if ctx.message.mentions:
            for user in ctx.message.mentions:
                if user.voice and user.voice.channel and user.voice.channel.id == destination.id:
                    try:
                        await user.move_to(None)
                        kicked += 1
                    except:
                        raise

        else:
            if destination.members:
                for user in destination.members:
                    try:
                        await user.move_to(None)
                        kicked += 1
                    except:
                        raise 
            else:
                await ctx.send("empty_channel")
                return

        await ctx.send(f"{get_text('kicked')}: {kicked}")

    @command(name="move", aliases=["m", "mv"])
    async def move(self, ctx, option: str = None, arg_source: typing.Optional[str] = "",
                   arg_destination: typing.Optional[str] = "", *, users: typing.Optional[str] = ""):
        get_destination = None
        get_source = None
        a = False
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
                    await ctx.send(get_text("no_channel_error"))
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
                    await ctx.send(get_text("no_channel_error"))
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
        if source is None or not destination:
            await ctx.send(get_text("no_channel_error"))
            return
        users_ids_list = None
        force_all = False
        if users != "":
            users = users.replace(",", "").replace("<@!", " ").replace(">", "").replace("\n", "")
            users = " ".join(users.split())
            users_ids_list = users.split(" ")
        else:
            force_all = True

        for mem in source.members:

            if force_all is True or Moderation.have_match(users_ids_list, mem.id) == a:
                await mem.move_to(destination)
                print("<INFO> Moved user: " + str(mem) + " to " + str(destination))

        pass

    pass
