import typing

from discord import VoiceChannel, Member, HTTPException
from discord.ext.commands import Cog, Context, group, guild_only

from bender.utils import bender_utils as butils

__all__ = ['Moderation']

from bender.utils.bender_utils import bender_module, prefix as _prefix
from bender.utils.message_handler import get_text


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
    def convert_kick_args(ctx, args) -> (VoiceChannel, list, list):
        members, roles, destination = None, None, None
        if args:
            if '<@' in args:
                args = args.split('<@', 1)
                if len(ctx.message.mentions) > 0 or len(ctx.message.role_mentions) > 0:
                    members = ctx.message.mentions
                    roles = ctx.message.role_mentions
                else:
                    members, roles = None, None

                if len(args) > 1:
                    destination_name: str = args[0].strip()
                else:
                    destination_name: str = ""
            else:
                destination_name = args

            if not destination_name.isspace() and len(destination_name) > 0:
                destination = butils.get_channel(ctx, destination_name)


        else:
            destination: VoiceChannel = ctx.author.voice.channel if (
                    ctx.author.voice and ctx.author.voice.channel) else None

        return destination, members, roles

    @staticmethod
    async def channel_check(ctx: Context, destination,*, can_be_empty: bool = False):
        if not destination:
            await ctx.send(get_text("no_channel_error"))
            return False
        if not destination.permissions_for(ctx.me).move_members:
            await ctx.send(get_text("bot_missing_permissions_error"))
            return False
        if len(destination.members) == 0 and not can_be_empty:
            await ctx.send(get_text("empty_channel_error"))
            return False
        return True

    @staticmethod
    async def move_all_members_or_with_role(_from: VoiceChannel, _to: typing.Union[VoiceChannel, None],
                                            members: list = None, roles: list = None, inverted: bool = False):
        moved = 0
        if (members and len(members) > 0) or (roles and len(roles) > 0):
            for connected_member in _from.members:
                for marked_member in members:
                    if (marked_member.id == connected_member.id) != inverted:
                        try:
                            await connected_member.move_to(_to)
                            moved += 1
                            break
                        except HTTPException:
                            break
                else:
                    for role in roles:
                        if (role in connected_member.roles) != inverted:
                            try:
                                await connected_member.move_to(_to)
                                moved += 1
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
                    moved += 1
                except HTTPException:
                    raise

        return moved

    @group(name="kick", aliases=["k"], description=get_text("command_kick_description"),
           help=get_text("command_kick_help"), usage=f"[all/others] [{get_text('channel')}] [@{get_text('member')}]"
                                                     f" [@{get_text('member')}] [@{get_text('role')}]...")
    @guild_only()
    async def kick(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            await ctx.invoke(ctx.bot.get_command("kick all"), args=ctx.message.content)
        pass

    @staticmethod
    async def kick_command(ctx, args, *, inverted: bool = False):
        destination, members, roles = Moderation.convert_kick_args(ctx, args)

        if not await Moderation.channel_check(ctx, destination):
            return
        if len(destination.members) == 0:
            await ctx.send(get_text("channel_empty"))
            return
        if destination.permissions_for(ctx.author).move_members:
            to_kick = len(destination.members)
            kicked = await Moderation.move_all_members_or_with_role(destination, None, members, roles, inverted=inverted)
            await ctx.send(get_text("%s kicked") % f"{kicked}/{to_kick}")

        else:
            await ctx.send("user_missing_permissions_error")
            return

    @kick.command(name='all', aliases=['a', ''], description=get_text("command_kick_all_description"),
                  help=get_text("command_kick_all_help"), usage=f"[{get_text('channel')}] [@{get_text('member')}]"
                                                                f"[@{get_text('member')}] [@{get_text('role')}]...")
    async def all(self, ctx: Context, *, args: typing.Optional[str] = None):
        await Moderation.kick_command(ctx, args)

    @kick.command(name='others', aliases=['o'], description=get_text("command_kick_others_description"),
                  help=get_text("command_kick_others_help"))
    async def others(self, ctx: Context, *, args: typing.Optional[str] = None):
        await Moderation.kick_command(ctx, args, inverted=True)

    @group(name="move", aliases=["mv"], description=get_text("command_move_description"),
           help=get_text("command_move_help"), usage=f"[all/others] "
                                                     f"[{get_text('source_channel')}] "
                                                     f"<{get_text('destination_channel')}> "
                                                     f"<@{get_text('member')}>"
                                                     f"<@{get_text('member')}> <@{get_text('role')}>...")
    @guild_only()
    async def move(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            args = ctx.message.content.replace(_prefix(message=ctx.message), '')
            if args[:2] == 'mv':
                args = args[2:].lstrip()
            elif args[:4] == 'move':
                args = args[:4].lstrip()
            else:
                return
            await ctx.invoke(ctx.bot.get_command('move all'),
                             args = args)
        pass

    @staticmethod
    async def move_command(ctx, args, inverted: bool = False):
        if args and ';' in args:
            args = args.split(';')
            if len(args) > 2:
                await ctx.send(get_text("move_all_use_chars_instead"))
                return

            _from = butils.get_channel(ctx, args[0].strip())
            if "<@" in args[1]:
                _to, members, roles = Moderation.convert_kick_args(ctx, args)

            else:
                members, roles = None, None
                _to = butils.get_channel(ctx, args[1].strip())

            if not _from:
                _from = butils.get_channel(ctx, args[0].replace('>!', '>'))
        else:
            _from = ctx.author.voice.channel if ctx.author.voice and ctx.author.voice.channel else None
            _to, members, roles = Moderation.convert_kick_args(ctx, args)

        if await Moderation.channel_check(ctx, _from) and await Moderation.channel_check(ctx, _to, can_be_empty=True):
            to_move = len(_from.members)
            moved = await Moderation.move_all_members_or_with_role(_from, _to, members, roles, inverted)
            await ctx.send(get_text("%s moved") % f"{moved}/{to_move}")

    @move.command(name='all', aliases=['a', ''], description=get_text("command_kick_all_description"),
                  help=get_text("command_kick_all_help"), usage=f"[{get_text('source_channel')};] "
                                                                f"<{get_text('destination_channel')}> "
                                                                f"<@{get_text('member')}> "
                                                                f"<@{get_text('member')}> <@{get_text('role')}>...")
    async def all(self, ctx: Context, *, args: typing.Optional[str] = None):
        await self.move_command(ctx, args)

    @move.command(name='others', aliases=['o'], description=get_text("command_kick_all_description"),
                  help=get_text("command_kick_all_help"), usage=f"[{get_text('source_channel')};] "
                                                                f"<{get_text('destination_channel')}> "
                                                                f"<@{get_text('member')}> "
                                                                f"<@{get_text('member')}> <@{get_text('role')}>...")
    async def others(self, ctx: Context, *, args: typing.Optional[str] = None):
        await self.move_command(ctx, args, True)
