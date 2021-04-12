import typing

import discord
from discord.ext import commands

import bender.utils.utils as butils

__all__ = ['VoiceClientCommands']

from bender.global_settings import DEBUG


class VoiceClientCommands(commands.Cog, name="Voice client"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="join", aliases=["j", "summon"])
    @commands.check(commands.cooldown(1, 10, commands.BucketType.user) or DEBUG)
    async def _join(self, ctx, channel: typing.Optional[str] = None):
        if channel is not None:
            if isinstance(channel, discord.VoiceChannel):
                destination = channel
            else:
                destination = butils.get_channel(ctx, channel)

        elif ctx.author.voice and ctx.author.voice.channel:
            destination = ctx.author.voice.channel
        else:
            await ctx.send("not_specified_channel")
            return

        if ctx.voice_client and ctx.voice_client.is_connected() and channel is None:
            if ctx.voice_client.channel == ctx.author.voice.channel:
                await ctx.send("already_in_same_channel")
                return
            else:
                try:
                    await ctx.voice_client.move_to(destination)
                    await ctx.send("joined " + destination.name)

                except:
                    await ctx.send("unknown_error_join")
                return

        try:
            await destination.connect()
            await ctx.send("joined " + destination.name)
            print("<INFO> Joined channel " + destination.name + "#" + str(destination.id))

        except:
            if destination is None:
                print("<ERROR> Error occurred while joining channel: no channel specified or user is not in channel")
            else:
                print("<ERROR> Error occurred while joining " + destination.name + "#" + str(destination.id))
            await ctx.send("unknown_error_join")

    @commands.command(name="leave", aliases=["dis", "disconnect", "l"])
    @commands.check(commands.cooldown(1, 10, commands.BucketType.user) or DEBUG)
    async def _leave(self, ctx):
        if ctx.voice_client:
            if ctx.voice_client.is_connected:
                try:
                    await ctx.voice_client.move_to(None)
                except Exception as e:
                    await ctx.send("leave_error")
                    print(e)
                return
        await ctx.send("not_connected_error")

class YoutubeMusic(commands.Cog, name = "Youtube Music"):
    def __init__(self, bot):
        self.bot = bot
        self.players = []

    @commands.command(name="play", aliases=["p"])
    async def _play(self, ctx, *, what: str):
        if not ctx.voice_client:
            if ctx.author.voice.channel:
                await ctx.invoke(VoiceClientCommands._join, ctx, channel = ctx.author.voice.channel)
        elif ctx.voice_client and ctx.voice_client.is_connected:
            if ctx.author.voice.channel and ctx.voice_client.channel.id != ctx.author.voice.channel.id:
                await ctx.send("playing_in_different_channel")
                return
        #check if music player for that guild exist



        pass
