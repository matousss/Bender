import typing

from discord import VoiceChannel, Member, HTTPException
from discord.ext.commands import Cog, Context, group, guild_only

from bender.utils import bender_utils as butils

__all__ = ['Moderation']

from bender.utils.bender_utils import bender_module
from bender.utils.message_handler import get_text


# todo check user permissions

@bender_module
class Moderation(Cog, name="Moderation", description=get_text("cog_moderation_description")):

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

    @staticmethod
    def convert_kick_args(ctx, args):
        if args:
            print(args)
            if '<@' in args:
                args = args.split('<@', 1)
                if len(args) > 1:
                    destination: str = args[0].strip()
                    args = args[1]
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
        if args:
            args = args.split("<@")
        roles = ctx.message.role_mentions
        members = ctx.message.mentions

        return destination, members, roles

    @staticmethod
    async def kick_checks(ctx: Context, destination):
        if not destination:
            await ctx.send(get_text("no_channel_error"))
            return False
        if not destination.permissions_for(ctx.me).move_members:
            await ctx.send(get_text("bot_missing_permissions_error"))
            return False
        if len(destination.members) == 0:
            await ctx.send(get_text("empty_channel_error"))
            return False
        return True

    @staticmethod
    async def move_all_members_or_with_role(_from: VoiceChannel, _to: typing.Union[VoiceChannel, None],
                                            members: list = None, roles: list = None, inverted: bool = False):
        kicked = 0
        if (members and len(members) > 0) or (roles and len(roles) > 0):
            for connected_member in _from.members:
                for marked_member in members:
                    if (marked_member.id == connected_member.id) != inverted:
                        try:
                            await connected_member.move_to(_to)
                            kicked += 1
                            break
                        except HTTPException:
                            break
                else:
                    for role in roles:
                        if (role in connected_member.roles) != inverted:
                            try:
                                await connected_member.move_to(_to)
                                kicked += 1
                                break
                            except HTTPException:
                                break
                    continue
                members.remove(marked_member)

        else:
            marked = _from.members.copy()
            for marked_member in marked:
                marked_member: Member
                try:
                    await marked_member.move_to(_to)
                    kicked += 1
                except HTTPException:
                    raise

        return kicked

    @group(name="kick", aliases=["k"], description=get_text("command_kick_description"),
           help=get_text("command_kick_help"), usage=f"[all/others] [{get_text('channel')}] <@{get_text('member')}>"
                                                     f"<@{get_text('member')}> <@{get_text('role')}>...")
    @guild_only()
    async def kick(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.all)
        pass

    @kick.command(name='all', aliases=['a'], description=get_text("command_kick_all_description"),
                  help=get_text("command_kick_all_help"), usage=f"[{get_text('channel')}] <@{get_text('member')}>"
                                                                f"<@{get_text('member')}> <@{get_text('role')}>...")
    async def all(self, ctx: Context, *, members: typing.Optional[str] = None):
        destination, members, roles = Moderation.convert_kick_args(ctx, members)
        if not await Moderation.kick_checks(ctx, destination):
            return

        if destination.permissions_for(ctx.author).move_members:
            to_kick = len(members) if members else len(destination.members)
            kicked = await Moderation.move_all_members_or_with_role(destination, None, members, roles)

            await ctx.send(get_text("%s kicked") % f"{kicked}/{to_kick}")

        else:
            await ctx.send("user_missing_permissions_error")
            return

    @kick.command(name='others', aliases=['o'], description=get_text("command_kick_others_description"),
                  help=get_text("command_kick_others_help"))
    async def others(self, ctx: Context, *, args: typing.Optional[str] = None):
        destination, members, roles = Moderation.convert_kick_args(ctx, args)

        if not await Moderation.kick_checks(ctx, destination):
            return
        if destination.permissions_for(ctx.author).move_members:
            to_kick = len(destination.members)
            kicked = await Moderation.move_all_members_or_with_role(destination, None, members, roles, inverted=True)
            await ctx.send(get_text("%s kicked") % f"{kicked}/{to_kick}")

        else:
            await ctx.send("user_missing_permissions_error")
            return

    # todo rewrite
    @group(name="move", aliases=["mv"], description=get_text("command_move_description"),
           help=get_text("command_move_help"), usage=f"[all/others] "
                                                     f"[{get_text('source_channel')}] "
                                                     f"<{get_text('destination_channel')}> "
                                                     f"<@{get_text('member')}>"
                                                     f"<@{get_text('member')}> <@{get_text('role')}>...")
    @guild_only()
    async def move(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.all)
        pass

    @move.command(name='all', aliases=['a'], description=get_text("command_kick_all_description"),
                  help=get_text("command_kick_all_help"), usage=f"[{get_text('source_channel')}] "
                                                                f"<{get_text('destination_channel')}> "
                                                                f"<@{get_text('member')}>"
                                                                f"<@{get_text('member')}> <@{get_text('role')}>...")
    async def all(self, ctx: Context, *, members: typing.Optional[str] = None):
        pass

    @move.command(name='others', aliases=['o'], description=get_text("command_kick_all_description"),
                  help=get_text("command_kick_all_help"), usage=f"[{get_text('source_channel')}] "
                                                                f"<{get_text('destination_channel')}> "
                                                                f"<@{get_text('member')}>"
                                                                f"<@{get_text('member')}> <@{get_text('role')}>...")
    async def others(self, ctx: Context, *, members: typing.Optional[str] = None):
        pass
