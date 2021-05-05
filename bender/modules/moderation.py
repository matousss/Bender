import typing

import discord.utils as discord_utils
from discord import VoiceChannel, Member, HTTPException, Message
from discord.ext.commands import Context, group, guild_only, MissingRequiredArgument
from bender.utils.bender_utils import BenderCog

__all__ = ['Moderation']


def setup(bot):
    bot.add_cog(Moderation(bot))


#
#
#
#
#
#
#
#
#
#


class Moderation(BenderCog, name="Moderation", description="cog_moderation_description"):

    def __init__(self, bot):
        self.bot = bot
        super().__init__(bot)

    @staticmethod
    async def channel_check(ctx: Context, destination, *, can_be_empty: bool = False):
        if not destination:
            await ctx.send(ctx.bot.get_text("no_channel_error", await ctx.bot.get_language(ctx)))
            return False
        if not destination.permissions_for(ctx.me).move_members:
            await ctx.send(ctx.bot.get_text("bot_missing_permissions_error", await ctx.bot.get_language(ctx)))
            return False
        if len(destination.members) == 0 and not can_be_empty:
            await ctx.send(ctx.bot.get_text("empty_channel_error", await ctx.bot.get_language(ctx)))
            return False
        return True

    @staticmethod
    async def move_all_members_or_with_role(_from: VoiceChannel, _to: typing.Union[VoiceChannel, None],
                                            members: list = None, roles: list = None, inverted: bool = False):
        moved = 0
        _marked_member = None
        if (members and len(members) > 0) or (roles and len(roles) > 0):
            for connected_member in _from.members:
                for marked_member in members:
                    if (marked_member.id == connected_member.id) != inverted:
                        _marked_member = marked_member
                        try:
                            await connected_member.move_to(_to)
                            moved += 1
                            break
                        except HTTPException:
                            break
                else:
                    if roles:
                        for role in roles:
                            if (role in connected_member.roles) != inverted:
                                try:
                                    await connected_member.move_to(_to)
                                    moved += 1
                                    break
                                except HTTPException:
                                    break
                        continue
                if _marked_member and not inverted:
                    members.remove(_marked_member)

        elif not inverted:
            marked = _from.members.copy()
            for marked_member in marked:
                marked_member: Member
                try:
                    await marked_member.move_to(_to)
                    moved += 1
                except HTTPException:
                    raise

        return moved

    # https://stackoverflow.com/questions/3675318/how-to-replace-the-some-characters-from-the-end-of-a-string
    @staticmethod
    def replace_last(source_string, replace_what, replace_with):
        head, _sep, tail = source_string.rpartition(replace_what)
        return head + replace_with + tail

    @staticmethod
    def get_raw_channels(message: Message, source_string):
        channel_names = source_string
        for mention in message.mentions:
            channel_names = Moderation.replace_last(channel_names, f'<@!{mention.id}>', '')
        for mention in message.role_mentions:
            channel_names = Moderation.replace_last(channel_names, f'<@&{mention.id}>', '')
        return channel_names

    @group(name="kick", aliases=["k"], description="command_kick_description",
           usage="command_kick_usage")
    @guild_only()
    async def kick(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            if ctx.message:
                args = ctx.message.content.replace(ctx.bot.get_prefix(ctx.message), '')
                if args[0] == 'k':
                    args = args[2:].lstrip()
                elif args[:4] == 'kick':
                    args = args[:4].lstrip()
                else:
                    return

                await ctx.invoke(ctx.bot.get_command('kick all'), args=args)

        pass

    @staticmethod
    async def kick_command(ctx, args, *, inverted: bool = False):
        destination_name = Moderation.get_raw_channels(ctx.message, args)
        destination = discord_utils.get(ctx.guild.channels, name=destination_name)
        members = ctx.message.mentions
        roles = ctx.message.role_mentions

        if not destination:
            destination: VoiceChannel = ctx.author.voice.channel if (
                    ctx.author.voice and ctx.author.voice.channel) else None
        if not await Moderation.channel_check(ctx, destination):
            return
        if len(destination.members) == 0:
            await ctx.send(ctx.bot.get_text("channel_empty", await ctx.bot.get_language(ctx)))
            return
        if len(members) == 0 and inverted:
            members = [ctx.author]
        if destination.permissions_for(ctx.author).move_members:
            to_kick = len(destination.members)
            kicked = await Moderation.move_all_members_or_with_role(destination, None, members, roles,
                                                                    inverted=inverted)
            await ctx.send(ctx.bot.get_text("%s %s kicked",
                                            await ctx.bot.get_language(ctx)) % (f"``{kicked}/{to_kick}``",
                                                                                f"``{destination.name}``"))

        else:
            await ctx.send("user_missing_permissions_error")
            return

    @kick.command(name='all', aliases=['a', ' '], description="command_kick_all_description",
                  usage="command_kick_all_usage")
    async def kick_all(self, ctx: Context, *, args: typing.Optional[str] = None):
        await Moderation.kick_command(ctx, args)

    @kick.command(name='others', aliases=['o'], description="command_kick_others_description",
                  usage="command_kick_others_usage")
    async def kick_others(self, ctx: Context, *, args: typing.Optional[str] = None):
        print("makám")
        await Moderation.kick_command(ctx, args, inverted=True)

    @group(name="move", aliases=["mv"], description="command_move_description",
           usage="command_move_usage")
    @guild_only()
    async def move(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            if ctx.message:
                args = ctx.message.content.replace(await ctx.bot.get_prefix(message=ctx.message), '')
                if args[:2] == 'mv':
                    args = args[2:].lstrip()
                elif args[:4] == 'move':
                    args = args[:4].lstrip()
                else:
                    return
                await ctx.invoke(ctx.bot.get_command('move all'),
                                 args=args)
        pass

    @staticmethod
    async def move_command(ctx, args, inverted: bool = False):
        channel_names_raw = Moderation.get_raw_channels(ctx.message, args)
        if not channel_names_raw:
            raise MissingRequiredArgument("destination channel")

        if channel_names_raw and ';' in channel_names_raw:
            channel_names = channel_names_raw.split(';', 1)
            _from = discord_utils.get(ctx.guild.channels, name=channel_names[0].strip())
            _to = discord_utils.get(ctx.guild.channels, name=channel_names[1].strip())
            if not _from:
                _from = discord_utils.get(ctx.guild.channels, name=channel_names[0].replace('.|', ';').lstrip())
            if not _to:
                _to = discord_utils.get(ctx.guild.channels, name=channel_names[1].replace('.|', ';').lstrip())

        else:
            _from = ctx.author.voice.channel if ctx.author.voice and ctx.author.voice.channel else None
            _to = discord_utils.get(ctx.guild.channels, name=channel_names_raw.strip())
            if not _to:
                _to = discord_utils.get(ctx.guild.channels, name=channel_names_raw.replace('.|', ';').strip())

        members = ctx.message.mentions
        roles = ctx.message.role_mentions

        if _from and _to and _from.id == _to.id:
            await ctx.send(ctx.bot.get_text("same_channels_error", await ctx.bot.get_language(ctx)))
            return
        if inverted and len(members) == 0:
            members = [ctx.author]
        if await Moderation.channel_check(ctx, _from) and await Moderation.channel_check(ctx, _to, can_be_empty=True):
            to_move = len(_from.members)
            moved = await Moderation.move_all_members_or_with_role(_from, _to, members, roles, inverted=inverted)
            await ctx.send(ctx.bot.get_text("%s %s moved", await ctx.bot.get_language(ctx)) % (f"``{moved}/{to_move}``",
                                                                                               f"``{_to.name}``"))

    @move.command(name='all', aliases=['a', ' '], description="command_move_all_description",
                  usage="command_move_all_usage")
    async def move_all(self, ctx: Context, *, args: typing.Optional[str] = None):
        await self.move_command(ctx, args)

    @move.command(name='others', aliases=['o'], description="command_move_others_description",
                  usage="command_move_others_usage")
    async def move_others(self, ctx: Context, *, args: typing.Optional[str] = None):
        await self.move_command(ctx, args, True)
