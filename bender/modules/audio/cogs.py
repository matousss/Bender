import asyncio
import datetime
import functools
import typing
from asyncio import QueueEmpty
from asyncio.queues import QueueFull

from discord import Embed, Color, VoiceChannel, ClientException
from discord.ext import commands
from discord.ext.commands import BucketType

import bender.utils.utils as butils
from bender.global_settings import MAX_SONG_DURATION

__all__ = ['VoiceClientCommands', 'YoutubeMusic']


from bender.global_settings import DEBUG
from bender.modules.audio.music import MusicPlayer, MusicSearcher
from bender.modules.audio.song import Song


class VoiceClientCommands(commands.Cog, name="Voice client"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="join", aliases=["j", "summon"])
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def _join(self, ctx, channel: typing.Optional[str] = None):
        if channel is not None:
            if isinstance(channel, VoiceChannel):
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

        except Exception as e:
            if destination is None:
                print("<ERROR> Error occurred while joining channel: no channel specified or user is not in channel")
            else:
                print("<ERROR> Error occurred while joining " + destination.name + "#" + str(destination.id))
            await ctx.send("unknown_error_join")
            print(e)

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


class YoutubeMusic(commands.Cog, name="Youtube Music"):
    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    @commands.command(name="zmk", aliases=["za"])
    async def _zmk(self, ctx):
        player = self.players[str(ctx.guild.id)]
        await ctx.send(player.lock.locked())
        await ctx.send(str(player.now_playing))

    @commands.command(name="play", aliases=["p"])
    @commands.cooldown(1, 3, type=BucketType.guild)
    async def _play(self, ctx, *, what: str):
        print("started")
        # check if in voice channel, connect to some if not
        if not ctx.voice_client or not ctx.voice_client.is_connected():
            if ctx.author.voice.channel:

                await ctx.invoke(VoiceClientCommands._join, ctx, channel=ctx.author.voice.channel)
                if ctx.voice_client and not ctx.voice_client.is_connected():
                    return
            else:
                await ctx.send("user_not_connected")

        # check if music player for that guild exist and get it or create new player
        player = None
        try:
            player = self.players[str(ctx.guild.id)]
        except KeyError:
            self.players[str(ctx.guild.id)] = MusicPlayer(ctx.voice_client)
            player = self.players[str(ctx.guild.id)]
        await player.lock.acquire()
        # todo send embed messages
        try:
            if ctx.voice_client and ctx.voice_client.is_connected:
                if ctx.author.voice.channel:
                    if ctx.voice_client.channel.id != ctx.author.voice.channel.id:
                        await ctx.send("playing_in_different_channel")
                else:
                    await ctx.send("user_not_connected")
                    return
            # find song
            await ctx.send("searching")

            loop = asyncio.get_running_loop()

            task = loop.run_in_executor(None, functools.partial(MusicSearcher.search_song, what))

            # task = player.searcher.search_song_async(what)
            song = await asyncio.wait_for(task, timeout=None)
            if not song:
                await ctx.send("not_found")

            await ctx.send("found")

            # check if song isn't too long
            def check_too_long(song_to_check: Song) -> bool:
                if song_to_check.details['duration'] > 0 and song_to_check.details['duration'] > MAX_SONG_DURATION:
                    return True
                return False

            if isinstance(song, Song):
                if check_too_long(song):
                    await ctx.send("error_too_long " + YoutubeMusic.format_song_details(song))
                    return
            elif isinstance(song, type([])):

                for s in song:
                    if check_too_long(s):
                        await ctx.send("error_too_long " + YoutubeMusic.format_song_details(song))
                        song.remove(s)

            else:
                raise TypeError(
                    f'song must be {Song.__name__} or {list.__name__}, but instead got {song.__class__.__name__}')

            if isinstance(song, list):

                count = len(song)
                first = song.pop(0)

                try:
                    await player.add_song(first)
                except QueueFull:
                    await ctx.send(f"queue_full (some song weren't add ({len(song) + 1}))")
                    return

                try:
                    last_added = await player.add_songs(song)
                except QueueFull:
                    # todo napsat kolik bylo přidáno a kolik ne (field v embed)
                    await ctx.send(f"queue_full (some song weren't add ({len(song)}))")
                    return
                await ctx.send(f"added_to_queue: {count - len(song)}")  # todo embed
            else:
                try:
                    await player.add_song(song)
                except QueueFull:
                    await ctx.send("queue_full")
                    return
                await ctx.send("added_to_queue")  # todo embed
            # kdyby došlo k odpojení během procesu
            if not ctx.voice_client or not ctx.voice_client.is_connected():
                if ctx.author.voice.channel:

                    await ctx.invoke(VoiceClientCommands._join, ctx, channel=ctx.author.voice.channel)
                    if not ctx.voice_client.is_connected():
                        return

            if not ctx.voice_client.is_playing():
                await player.play()

        finally:
            player.lock.release()
            print("ended")

    # todo fix
    @commands.command(name='skip', aliases=['s'])
    async def _skip(self, ctx, count: typing.Optional[int] = 1):
        # todo skip <count>
        if ctx.voice_client and ctx.voice_client.is_playing():
            player = self.players[str(ctx.guild.id)]
            await player.lock.acquire()
            if player.now_playing:
                a = 1
            else:
                a = 0
            qsize = player.qsize() + a
            try:

                if count <= len(player) + a:

                    try:
                        if player.now_playing:
                            player.remove(count - 1)
                            await ctx.voice_client.stop()
                        else:
                            player.remove(count)

                    except QueueEmpty:
                        pass
                    except ClientException:
                        pass
                    finally:
                        return
                else:
                    await ctx.send("<warning>_parameter_out_of_bounds -> skipping all")

                    while not player.queue_empty():
                        try:
                            player.remove()
                        except QueueEmpty:
                            break
                    try:
                        ctx.voice_client.stop()
                    except ClientException:
                        pass
                    finally:
                        return
            finally:
                player.lock.release()
                await ctx.send(f"skipped : {qsize - player.qsize()}")
        await ctx.send("error_not_playing")

    # todo remove from queue command
    # todo loop command
    # todo pause, resume cmd

    @staticmethod
    def format_song_details(song: Song) -> str:
        title = song.details['title']
        duration = song.details['duration']

        return f"``{title if title else '<unknown>'} [{str(datetime.timedelta(seconds=duration)) if duration > 0 else '<unknown>'}]``"

    @commands.command(name='now playing', aliases=['np'])
    async def _nowplaying(self, ctx):

        if ctx.voice_client and ctx.voice_client.is_playing():
            try:
                player = self.players[str(ctx.guild.id)]
            except KeyError:
                ctx.send("unknown_error")
                return
            if player.now_playing:
                await ctx.send(f"now_playing {YoutubeMusic.format_song_details(player.now_playing)}")
                return

        await ctx.send("error_not_playing")

    @commands.command(name='queue', aliases=['q'])
    async def _queue(self, ctx):
        try:
            player = self.players[str(ctx.guild.id)]

        except KeyError:
            await ctx.send("not_playing")
            return
        queue = await player.current_queue()
        embeds = []
        embeds.append(Embed(color=Color.red()))
        embed = embeds[0]
        embeds_count = 0
        if player.now_playing:
            embed.add_field(name="Now playing:", value=YoutubeMusic.format_song_details(player.now_playing),
                            inline=False)

        index = 0
        sb = "Wow, such empty"

        try:
            index += 1
            sb = f"{index}. {YoutubeMusic.format_song_details(queue.popleft())}"

        except Exception as e:
            raise e

        for song in queue:
            index += 1
            embed.add_field(name="\u200b", value=f"\n{index}. {YoutubeMusic.format_song_details(song)}", inline=False)

            if index % 20 == 0:
                embeds.append(Embed(color=Color.red()))
                embeds_count += 1
                embed = embeds[embeds_count]

            if index == 20:
                embed.insert_field_at(index=1, name=f"In queue is currently [{(len(queue) + 1)}] song/s:", value=sb)

        if index < 20:
            embed.insert_field_at(index=1, name=f"In queue is currently [{(len(queue) + 1)}] song/s:", value=sb)

        for e in embeds:
            await ctx.send(embed=e)
