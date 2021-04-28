import asyncio
import traceback
import typing

from discord import VoiceChannel, ClientException
from discord.ext.commands import Cog, BucketType, command, cooldown, Context, guild_only, BotMissingPermissions

from global_settings import DEBUG
from utils import utils as butils
from utils.utils import bender_module, BenderModuleError
from utils.message_handler import get_text

try:
    import nacl.secret
    is_nacl = True
except ImportError:
    is_nacl = False

@bender_module
class VoiceClientCommands(Cog, name="Voice client"):
    def __init__(self, bot):
        if not is_nacl:
            raise BenderModuleError(f"{self.__class__.__name__} requires PyNaCl library to work with "
                                    f"discord.VoiceClient")
        self.bot = bot
        print(f"Initialized {str(__name__)}")

    @command(name="join", aliases=["j", "summon"])
    @guild_only()
    # @bot_has_guild_permissions(connect=True, speak=True)
    @cooldown(1, 10, BucketType.guild)
    async def join(self, ctx: Context, channel: typing.Optional[str] = None):
        if ctx.voice_client and ctx.voice_client.is_connected():
            raise ClientException("Already connected to voice channel")

        if channel is not None:
            if isinstance(channel, VoiceChannel):
                destination = channel
            else:
                destination = butils.get_channel(ctx, channel)
                if not destination:
                    await ctx.send(f'{get_text("no_channel")}: {channel}')
                    return

        elif ctx.author.voice and ctx.author.voice.channel:
            destination = ctx.author.voice.channel
        else:
            await ctx.send(get_text("channel_not_specified"))
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

        if destination.permissions_for(ctx.me).connect is False or destination.permissions_for(ctx.me).speak is False:
            # await ctx.send(get_text('missing_permissions_error'))
            raise BotMissingPermissions()
            return
        try:
            await destination.connect(timeout=10)
            await ctx.send(f"{get_text('join')} {destination.name}")
            print("<INFO> Joined channel " + destination.name + "#" + str(destination.id))
        except asyncio.TimeoutError as e:
            await ctx.send(get_text("timeout_error"))
            return
        except ClientException:
            await ctx.send("already_connected_error")
            print("<ERROR> Error occurred while joining " + destination.name + "#" + str(destination.id))
            return


    @command(name="disconnect", aliases=["dis", "leave", "l"])
    @cooldown(1, 10, BucketType.user)
    async def disconnect(self, ctx):
        if ctx.voice_client:
            if ctx.voice_client.is_connected:
                try:
                    await ctx.voice_client.move_to(None)
                except Exception as e:
                    await ctx.send(get_text("leave_error"))
                    traceback.print_exc()
                return
        await ctx.send(get_text("no_channel_error"))
