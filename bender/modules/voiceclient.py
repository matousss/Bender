import asyncio
import typing
from datetime import datetime

import discord
from discord import VoiceChannel, ClientException
from discord.ext.commands import BucketType, command, cooldown, Context

import bender.utils.message_handler
from bender.bot import BenderCog
from bender.utils.bender_utils import ExtensionInitializeError

try:
    import nacl.secret

    is_nacl = True
except ImportError:
    is_nacl = False


def setup(bot):
    bot.add_cog(VoiceClientCommands(bot))


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


class VoiceClientCommands(BenderCog, name="Voice client", description="cog_voiceclientcommands_description"):
    def __init__(self, bot):
        """
        Parameters
        ----------
        bot : Bender
            Bot to which is cog added
            Must be :class: ``Bender`` or child of :class: ``Cog``, with implemented methods `get_text, get_language`
        """

        if not is_nacl:
            raise ExtensionInitializeError(
                f"{self.__class__.__name__} requires PyNaCl library to work with "
                f"discord.VoiceClient")
        super().__init__(bot)

    @command(name="join", aliases=["j", "summon"], description="command_join_description",
             usage="command_join_usage")
    @cooldown(1, 2, BucketType.guild)
    async def join(self, ctx: Context, *, channel: typing.Optional[str] = None):
        """
        Command `join`

        Parameters
        ----------
        ctx : Context
        channel : str, optional
            Name of channel
       """
        destination = None
        if channel is not None:
            if isinstance(channel, VoiceChannel):
                destination = channel
            else:
                destination = discord.utils.get(ctx.guild.voice_channels, name=channel)


        elif ctx.author.voice and ctx.author.voice.channel:
            destination = ctx.author.voice.channel

        if not destination:
            await ctx.send(self.get_text("no_channel_error", await self.get_language(ctx)))
            return

        if destination.permissions_for(ctx.me).connect is False:
            raise bender.utils.bender_utils.BotMissingPermissions()
        if destination.permissions_for(ctx.me).speak is False:
            raise bender.utils.bender_utils.BotMissingPermissions()

        if ctx.voice_client and ctx.voice_client.is_connected() and destination:
            if ctx.voice_client.channel.id == destination.id:
                await ctx.send(self.get_text("join_error_same_channel", await self.get_language(ctx)))
                return
            else:
                lang = await self.get_language(ctx)
                try:
                    await ctx.voice_client.move_to(destination)
                    await ctx.send(f"{self.get_text('join', lang)} {destination.name}")

                except Exception:
                    print("<ERROR> Error occurred while joining " + destination.name + "#" + str(destination.id))
                    await ctx.send(self.get_text("unknown_join_error", lang))
                return



        try:
            if ctx.voice_client and ctx.voice_client.is_connected():
                await destination.move(timeout=10)
            else:
                await destination.connect(timeout=10)
            await ctx.send(self.get_text('%s join', await self.get_language(ctx)) % f"``{destination.name}``")
            print(f"<INFO> [{datetime.now().strftime('%H:%M:%S')}] Joined channel " + destination.name + "#" + str(
                destination.id))
        except asyncio.TimeoutError:
            await ctx.send(self.get_text("timeout_error", await self.get_language(ctx)))
            return
        except ClientException as e:
            raise e
            await ctx.send(self.get_text("already_connected_error", await self.get_language(ctx)))
            print("<ERROR> Error occurred while joining " + destination.name + "#" + str(destination.id))
            return

    @command(name="disconnect", aliases=["dis", "leave", "l"], description="command_disconnect_description",
             usage="")
    @cooldown(1, 5, BucketType.user)
    async def disconnect(self, ctx: Context):
        if ctx.voice_client:
            if ctx.voice_client.is_connected:
                try:
                    await ctx.voice_client.move_to(None)
                except Exception:
                    await ctx.send(self.get_text("leave_error", await self.get_language(ctx)))
                return
        await ctx.send(self.get_text("no_channel_error", await self.get_language(ctx)))
