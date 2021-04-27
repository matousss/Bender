import typing

from discord import VoiceChannel
from discord.ext.commands import Cog, command, Context, group, guild_only

from utils import utils as butils

__all__ = ['Moderation']

from utils.utils import bender_module
from utils.message_handler import get_text


# todo check user permissions

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
    @guild_only()
    async def kick(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.all)
        pass

    @staticmethod
    def convert_kick_args(ctx, args):
        # if args:
        #
        #     if '<@' in args:
        #         args = args.split('<@', 1)
        #         if len(args) > 1:
        #             destination: str = args[0]
        #             args = "".join(args[1].replace('>', '').split()).split('<@')
        #         else:
        #             destination: str = ""
        #             args = "".join(args[0].replace('>', '').split()).split('<@')
        #     else:
        #         destination = args
        #         args = None
        #
        #     print(args)
        #
        #     if not destination.isspace() and len(destination) > 0:
        #         destination = butils.get_channel(ctx, destination)
        #     else:
        #         destination: VoiceChannel = ctx.author.voice.channel if (
        #                 ctx.author.voice and ctx.author.voice.channel) else None
        # else:
        #     destination: VoiceChannel = ctx.author.voice.channel if (
        #             ctx.author.voice and ctx.author.voice.channel) else None
        if args:

            if '<@' in args:
                args = args.split('<@', 1)
                if len(args) > 1:
                    destination: str = args[0].strip()
                else:
                    destination: str = ""
            else:
                destination = args
                args = None



            if not destination.isspace() and len(destination) > 0:
                destination = butils.get_channel(ctx, destination)
            else:
                destination: VoiceChannel = ctx.author.voice.channel if (
                        ctx.author.voice and ctx.author.voice.channel) else None
        else:
            destination: VoiceChannel = ctx.author.voice.channel if (
                    ctx.author.voice and ctx.author.voice.channel) else None
        args = []
        for m in ctx.message.mentions:
            args.append(m.id)

        return destination, args

    @staticmethod
    async def kick_checks(ctx: Context, destination):
        if not destination:
            await ctx.send(get_text("not_channel_error"))
            return False
        if not destination.permissions_for(ctx.me).move_members:
            await ctx.send(get_text("bot_missing_permissions_error"))
            return False
        if len(destination.members) == 0:
            await ctx.send(get_text("empty_channel_error"))
            return False
        return True

    # todo https://discordpy.readthedocs.io/en/latest/ext/commands/commands.html
    @kick.command(aliases=['a'])
    async def all(self, ctx: Context, *, args: typing.Optional[str] = None):
        # if destination:
        #     if '<@' in destination:
        #         destination = destination.split('<@', 1)[0]
        #     destination = butils.get_channel(ctx, destination.lstrip())
        # else:
        #     if ctx.author.voice and ctx.author.voice.channel:
        #         destination = ctx.author.voice.channel
        #
        # if not destination:
        #     await ctx.send((get_text("no_channel_error")), reference=ctx.message, mention_author=False)
        #
        # return
        #
        # kicked = 0
        # if ctx.message.mentions:
        #     for user in ctx.message.mentions:
        #         if user.voice and user.voice.channel and user.voice.channel.id == destination.id:
        #             try:
        #                 await user.move_to(None)
        #                 kicked += 1
        #             except:
        #                 raise
        #
        # else:
        #     if destination.members:
        #         for user in destination.members:
        #             try:
        #                 await user.move_to(None)
        #                 kicked += 1
        #             except:
        #                 raise
        #     else:
        #         await ctx.send("empty_channel")
        #         return
        #
        # await ctx.send(f"{get_text('kicked')}: {kicked}")

        destination, args = Moderation.convert_kick_args(ctx, args)
        if not await Moderation.kick_checks(ctx, destination):
            return

        if destination.permissions_for(ctx.author).move_members:
            to_kick = len(args) if args else len(destination.members)
            kicked = 0
            if args and len(args) > 0:
                for member in destination.members:
                    for m in args:
                        if str(m) == str(member.id):
                            try:
                                await member.move_to(None)
                                kicked += 1
                            except:
                                pass
                            args.remove(m)
            else:
                marked = destination.members.copy()
                for m in marked:
                    try:
                        await m.move_to(None)
                        kicked += 1
                    except:
                        raise

            await ctx.send(get_text("%s kicked") % f"{kicked}/{to_kick}")

        else:
            await ctx.send("user_missing_permissions_error")
            return


    @kick.command(aliases=['o'])
    async def others(self, ctx: Context, *, args: typing.Optional[str] = None):
        destination, args = Moderation.convert_kick_args(ctx, args)

        if not await Moderation.kick_checks(ctx, destination):
            return
        if destination.permissions_for(ctx.author).move_members:
            to_kick = ((len(args) if args else (len(destination.members)) -
                                               (1 if ctx.author.voice.channel.id == destination.id else 0)))
            kicked = 0
            if args and len(args) > 0:
                for member in destination.members:
                    for m in args:
                        if str(m) == str(member.id):
                            break
                    else:
                        try:
                            await member.move_to(None)
                            kicked += 1
                        except:
                            pass

            else:
                for m in destination.members:
                    if m.id != ctx.author.id:
                        try:
                            await m.move_to(None)
                            kicked += 1
                        except:
                            raise

            await ctx.send(get_text("%s kicked") % f"{kicked}/{to_kick}")

        else:
            await ctx.send("user_missing_permissions_error")
            return

    # todo rewrite
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
