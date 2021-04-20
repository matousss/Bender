import traceback
import typing

from discord import VoiceChannel
from discord.ext.commands import Cog, BucketType, command, cooldown, check

from bender.global_settings import DEBUG
from bender.utils import utils as butils
from bender.utils.utils import bender_module
from bender.utils.message_handler import get_text

@bender_module
class VoiceClientCommands(Cog, name="Voice client"):
    def __init__(self, bot):
        self.bot = bot
        print(f"Initialized {str(__name__)}")

    @command(name="join", aliases=["j", "summon"])
    @cooldown(1, 10, BucketType.guild)
    async def join(self, ctx, channel: typing.Optional[str] = None):
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
                    await ctx.send(get_text("join_error_unknown"))
                return

        try:
            await destination.connect()
            await ctx.send(f"{get_text('join')} {destination.name}")
            print("<INFO> Joined channel " + destination.name + "#" + str(destination.id))

        except Exception as e:
            traceback.print_exc()
            if destination is None:
                print("<ERROR> Error occurred while joining channel: no channel specified or user is not in channel")
            else:
                print("<ERROR> Error occurred while joining " + destination.name + "#" + str(destination.id))
            await ctx.send(get_text("unknown_error_join"))
            traceback.print_exc()

    @command(name="disconnect", aliases=["dis", "leave", "l"])
    @check(cooldown(1, 10, BucketType.user) or DEBUG)
    async def disconnect(self, ctx):
        if ctx.voice_client:
            if ctx.voice_client.is_connected:
                try:
                    await ctx.voice_client.move_to(None)
                except Exception as e:
                    await ctx.send(get_text("leave_error"))
                    raise e
                return
        await ctx.send(get_text("no_channel_error"))
