import asyncio
import typing

import discord
from discord import VoiceChannel, ClientException
from discord.ext.commands import Cog, BucketType, command, cooldown, Context, guild_only

import bender.utils.bender_utils
import bender.utils.message_handler

get_text = bender.utils.message_handler.get_text

try:
    import nacl.secret

    is_nacl = True
except ImportError:
    is_nacl = False


@bender.utils.bender_utils.bender_module
class VoiceClientCommands(Cog, name="Voice client", description=get_text("cog_voiceclientcommands_desc")):
    def __init__(self, bot):
        if not is_nacl:
            raise bender.utils.bender_utils.BenderModuleError(
                f"{self.__class__.__name__} requires PyNaCl library to work with "
                f"discord.VoiceClient")
        self.bot = bot
        print(f"Initialized {str(__name__)}")

    @command(name="join", aliases=["j", "summon"], description=get_text("command_join_description"),
             help=get_text("command_join_help"))
    @guild_only()
    @cooldown(1, 10, BucketType.guild)
    async def join(self, ctx: Context, *, channel: typing.Optional[str] = None):
        if ctx.voice_client and ctx.voice_client.is_connected():
            # raise ClientException("Already connected to voice channel")
            await ctx.send(get_text("already_connected_error"))
        if channel is not None:
            if isinstance(channel, VoiceChannel):
                destination = channel
            else:
                destination = discord.utils.get(ctx.guild.channels, name=channel)
                if not destination:
                    await ctx.send(f'{get_text("no_channel")}: {channel}')
                    return

        elif ctx.author.voice and ctx.author.voice.channel:
            destination = ctx.author.voice.channel
        else:
            await ctx.send(get_text("no_channel_error"))
            return

        if ctx.voice_client and ctx.voice_client.is_connected() and channel is None:
            if ctx.voice_client.channel == ctx.author.voice.channel:
                await ctx.send(get_text("join_error_same_channel"))
                return
            else:
                try:
                    await ctx.voice_client.move_to(destination)
                    await ctx.send(f"{get_text('join')} {destination.name}")

                except Exception:
                    await ctx.send(get_text("unknow_join_error"))
                return

        if destination.permissions_for(ctx.me).connect is False:
            raise bender.utils.bender_utils.BotMissingPermissions()
        if destination.permissions_for(ctx.me).speak is False:
            raise bender.utils.bender_utils.BotMissingPermissions()

        try:
            await destination.connect(timeout=10)
            await ctx.send(f"{get_text('join')} {destination.name}")
            print("<INFO> Joined channel " + destination.name + "#" + str(destination.id))
        except asyncio.TimeoutError:
            await ctx.send(get_text("timeout_error"))
            return
        except ClientException:
            await ctx.send("already_connected_error")
            print("<ERROR> Error occurred while joining " + destination.name + "#" + str(destination.id))
            return

    @command(name="disconnect", aliases=["dis", "leave", "l"], description=get_text("command_leave_description"),
             help=get_text("command_leave_help"))
    @guild_only()
    @cooldown(1, 10, BucketType.user)
    async def disconnect(self, ctx: Context):
        if ctx.voice_client:
            if ctx.voice_client.is_connected:
                try:
                    await ctx.voice_client.move_to(None)
                except Exception:
                    await ctx.send(get_text("leave_error"))
                return
        await ctx.send(get_text("no_channel_error"))
