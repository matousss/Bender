import asyncio
import typing

import discord
from discord import VoiceChannel, ClientException
from discord.ext.commands import BucketType, command, cooldown, Context, guild_only

import bender.utils.bender_utils
import bender.utils.message_handler
from bender.bot import BenderCog, Bender as Bot

try:
    import nacl.secret

    is_nacl = True
except ImportError:
    is_nacl = False


def setup(bot: Bot):
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
    def __init__(self, bot: Bot):

        if not is_nacl:
            raise bender.utils.bender_utils.BenderModuleError(
                f"{self.__class__.__name__} requires PyNaCl library to work with "
                f"discord.VoiceClient")
        super().__init__(bot)

    @command(name="join", aliases=["j", "summon"], description="command_join_description",
             usage="command_join_usage")
    @guild_only()
    @cooldown(1, 10, BucketType.guild)
    async def join(self, ctx: Context, *, channel: typing.Optional[str] = None):
        if ctx.voice_client and ctx.voice_client.is_connected():
            # raise ClientException("Already connected to voice channel")
            await ctx.send(self.get_text("already_connected_error", await self.get_language(ctx)))
            return
        if channel is not None:
            if isinstance(channel, VoiceChannel):
                destination = channel
            else:
                destination = discord.utils.get(ctx.guild.channels, name=channel)
                if not destination:
                    await ctx.send(f'{self.get_text("no_channel", await self.get_language(ctx))}: {channel}')
                    return

        elif ctx.author.voice and ctx.author.voice.channel:
            destination = ctx.author.voice.channel

        else:
            await ctx.send(self.get_text("no_channel_error", await self.get_language(ctx)))
            return

        if ctx.voice_client and ctx.voice_client.is_connected() and channel is None:
            if ctx.voice_client.channel == ctx.author.voice.channel:
                await ctx.send(self.get_text("join_error_same_channel"))
                return
            else:
                lang = await self.get_language(ctx)
                try:
                    await ctx.voice_client.move_to(destination)
                    await ctx.send(f"{self.get_text('join', lang)} {destination.name}")

                except Exception:
                    await ctx.send(self.get_text("unknown_join_error", lang))
                return

        if destination.permissions_for(ctx.me).connect is False:
            raise bender.utils.bender_utils.BotMissingPermissions()
        if destination.permissions_for(ctx.me).speak is False:
            raise bender.utils.bender_utils.BotMissingPermissions()

        try:
            await destination.connect(timeout=10)
            await ctx.send(self.get_text('%s join', await self.get_language(ctx)) % f"``{destination.name}``")
            print("<INFO> Joined channel " + destination.name + "#" + str(destination.id))
        except asyncio.TimeoutError:
            await ctx.send(self.get_text("timeout_error", await self.get_language(ctx)))
            return
        except ClientException:
            await ctx.send(self.get_text("already_connected_error", await self.get_language(ctx)))
            print("<ERROR> Error occurred while joining " + destination.name + "#" + str(destination.id))
            return

    @command(name="disconnect", aliases=["dis", "leave", "l"], description="command_disconnect_description",
             usage="")
    @guild_only()
    @cooldown(1, 10, BucketType.user)
    async def disconnect(self, ctx: Context):
        if ctx.voice_client:
            if ctx.voice_client.is_connected:
                try:
                    await ctx.voice_client.move_to(None)
                except Exception:
                    await ctx.send(self.get_text("leave_error", await self.get_language(ctx)))
                return
        await ctx.send(self.get_text("no_channel_error", await self.get_language(ctx)))
