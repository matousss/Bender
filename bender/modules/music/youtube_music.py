from __future__ import annotations
import asyncio
import datetime
import functools
import traceback
import typing
from asyncio import QueueEmpty
from asyncio.queues import QueueFull

from discord import Embed, Color, ClientException
from discord.ext import commands
from discord.ext import tasks

from bender.global_settings import MAX_SONG_DURATION
from bender.modules.music.music import MusicPlayer, MusicSearcher
from bender.modules.music.song import Song
from bender.utils.utils import bender_module
from bender.utils.message_handler import get_text

__all__ = ['YoutubeMusic']


try:
    from bender.modules.voiceclient import VoiceClientCommands
except ImportError:
    from bender.utils.utils import BenderModuleError

    raise BenderModuleError(f"{__name__} requires VoiceClientCommands module to work")


@bender_module
class YoutubeMusic(commands.Cog, name="Youtube Music"):
    def __init__(self, bot):
        self.bot = bot
        self.players = {}
        print(f"Initialized {str(__name__)}")





    @commands.command(name="play", aliases=["p"])
    @commands.cooldown(1, 3, type=commands.BucketType.guild)
    async def play(self, ctx, *, what: str):
        print("started")
        # check if in voice channel, connect to some if not
        if not ctx.voice_client or not ctx.voice_client.is_connected():
            if ctx.author.voice and ctx.author.voice.channel:
                join = self.bot.get_command('join')
                if join:
                    await ctx.invoke(join, channel=ctx.author.voice.channel)
                else:
                    raise BenderModuleError("Tried invoke command join from modules.voiceclient.VoiceClientCommands but "
                                            "it doesn't exist")
            elif ctx.voice_client and not ctx.voice_client.is_connected():
                await ctx.send(get_text("no_channel_error"))
                return
            else:
                await ctx.send(get_text("not_connected_error"))
                return

        # check if music player for that guild exist and get it or create new player
        player = None
        if str(ctx.guild.id) in self.players.keys():
            player = self.players[str(ctx.guild.id)]
        else:
            self.players[str(ctx.guild.id)] = MusicPlayer(ctx.voice_client)
            player = self.players[str(ctx.guild.id)]
        await player.lock.acquire()
        # todo send embed messages
        try:
            if ctx.voice_client and ctx.voice_client.is_connected:
                if ctx.author.voice.channel:
                    if ctx.voice_client.channel.id != ctx.author.voice.channel.id:
                        await ctx.send(get_text("playing_error_different_channel"))
                else:
                    await ctx.send(get_text("user_not_connected"))
                    return
            # find song
            await ctx.send(get_text("searching"))

            loop = asyncio.get_running_loop()

            task = loop.run_in_executor(None, functools.partial(MusicSearcher.search_song, what))

            # task = player.searcher.search_song_async(what)
            song = await asyncio.wait_for(task, timeout=None)
            if not song:
                await ctx.send(get_text("not_found_error"))

            await ctx.send(get_text("found"))

            # check if song isn't too long
            def check_too_long(song_to_check: Song) -> bool:
                if song_to_check.details['duration'] > 0 and song_to_check.details['duration'] > MAX_SONG_DURATION:
                    return True
                return False

            if isinstance(song, Song):
                if check_too_long(song):
                    await ctx.send(f"{get_text('error_too_long')}  {YoutubeMusic.format_song_details(song)}")
                    return
            elif isinstance(song, type([])):
                for s in song:
                    if check_too_long(s):
                        await ctx.send(f"{get_text('error_too_long')}  {YoutubeMusic.format_song_details(s)}")
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
                    await ctx.send(f"{get_text('queue_full')} ({len(song) + 1})")
                    return

                try:
                    last_added = await player.add_songs(song)
                except QueueFull:
                    # todo napsat kolik bylo přidáno a kolik ne (field v embed)
                    await ctx.send(f"{get_text('queue_full')} ({len(song)})")
                    return
                await ctx.send(f"{get_text('added_to_queue')}: {count - len(song)}")  # todo embed
            else:
                try:
                    await player.add_song(song)
                except QueueFull:
                    await ctx.send(get_text("queue_full"))
                    return
                await ctx.send(get_text("added_to_queue"))  # todo embed
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
    async def skip(self, ctx, count: typing.Optional[int] = 1):
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
                    await ctx.send(get_text("queue_size_error"))

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
                await ctx.send(f"{get_text('skip')} : {qsize - player.qsize()}")
        await ctx.send(get_text("not_playing_error"))

    # todo remove from queue command
    # todo loop command
    # todo pause, resume cmd


    @staticmethod
    def format_song_details(song: Song) -> str:
        title = song.details['title']
        duration = song.details['duration']

        return f"``{title if title else '<NaN>'}" \
               f" [{str(datetime.timedelta(seconds=duration)) if duration > 0 else '<NaN>'}]``"

    @commands.command(name='now playing', aliases=['np'])
    async def nowplaying(self, ctx):

        if ctx.voice_client and ctx.voice_client.is_playing():
            # try:
            #     player = self.players[str(ctx.guild.id)]
            # except KeyError:
            #     traceback.print_exc()
            #     ctx.send(get_text("unknown_error"))
            #     return
            if str(ctx.guild.id) in self.players.keys():
                player = self.players[str(ctx.guild.id)]
            else:
                await ctx.send(get_text("not_playing_error"))
                return
            if player.now_playing:
                await ctx.send(f"{get_text('now_playing')} {YoutubeMusic.format_song_details(player.now_playing)}")
                return

        await ctx.send(get_text("error_not_playing"))

    @commands.command(name='queue', aliases=['q'])
    async def queue(self, ctx):
        # todo pages
        try:
            player = self.players[str(ctx.guild.id)]

        except KeyError:
            await ctx.send(get_text("not_playing_error"))
            return
        queue = await player.current_queue()
        embeds = [Embed(color=Color.red())]
        embed = embeds[0]
        embeds_count = 0
        if player.now_playing:
            embed.add_field(name=get_text("now_playing"), value=YoutubeMusic.format_song_details(player.now_playing),
                            inline=False)

        index = 0
        #sb = "Wow, such empty"
        sb = get_text('empty')
        try:
            index += 1
            first = f"{index}. {YoutubeMusic.format_song_details(queue.popleft())}"

        except Exception as e:
            raise e

        if first:
            sb = first

        for song in queue:
            index += 1
            embed.add_field(name="\u200b", value=f"\n{index}. {YoutubeMusic.format_song_details(song)}", inline=False)

            if index % 20 == 0:
                embeds.append(Embed(color=Color.red()))
                embeds_count += 1
                embed = embeds[embeds_count]

            if index == 20:
                embed.insert_field_at(index=1, name=f"{get_text('current_queue')} [{(len(queue) + 1)}] {get_text('song')}:", value=sb)

        if index < 20:
            embed.insert_field_at(index=1, name=f"{get_text('current_queue')} [{(len(queue) + 1)}] {get_text('song')}:", value=sb)

        for e in embeds:
            await ctx.send(embed=e)
