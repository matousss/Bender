from __future__ import annotations

import asyncio
import datetime
import functools
import logging
import math
import typing
import warnings
from asyncio import QueueEmpty
from asyncio.queues import QueueFull

from discord import Embed, Color, ClientException
from discord.ext import commands

from global_settings import MAX_SONG_DURATION
from modules.music.music import MusicPlayer, MusicSearcher
from modules.music.song import Song
from utils.checks import can_join_speak
from utils.message_handler import get_text
from utils.utils import bender_module

__all__ = ['YoutubeMusic']
logger = logging.getLogger('bender')

PAGE_SIZE = 10


@bender_module
class YoutubeMusic(commands.Cog, name="Youtube Music"):
    def __init__(self, bot):
        self.BOT: commands.Bot = bot
        self.players = {}
        self.join = None
        print(f"Initialized {str(__name__)}")

    # @commands.
    # def delete_player(self, key: str):
    @commands.Cog.listener()
    async def on_ready(self):
        self.join = self.BOT.get_command('join')

        if not self.join:
            self.BOT.remove_cog('Youtube Music')
            warning = f"Cog {self.__class__.__name__} was disabled! " \
                      f"That happened because cog {self.__class__.__name__} requires join command from " \
                      f"VoiceClientCommands "
            warnings.warn(warning)
            logger.warning(warning)

    @commands.command(name="play", aliases=["p"])
    @commands.check(can_join_speak)
    @commands.guild_only()
    @commands.cooldown(1, 3, type=commands.BucketType.guild)
    async def play(self, ctx, *, what: str):
        print("started")
        # check if in voice channel, connect to some if not
        if not ctx.voice_client or not ctx.voice_client.is_connected():
            if ctx.author.voice and ctx.author.voice.channel:

                await ctx.invoke(self.join, channel=ctx.author.voice.channel)

            elif ctx.voice_client and not ctx.voice_client.is_connected():
                await ctx.send(get_text("no_channel_error"))
                return
            else:
                await ctx.send(get_text("not_connected_error"))
                return

        # check if music player for that guild exist and get it or create new player
        if str(ctx.guild.id) in self.players.keys():
            player = self.players[str(ctx.guild.id)]
        else:
            self.players[str(ctx.guild.id)] = MusicPlayer(ctx.voice_client)
            player = self.players[str(ctx.guild.id)]
        # todo send embed messages

        async with player.lock:
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

            async def start_playing():
                # in case of unexpected disconnect
                if not ctx.voice_client or not ctx.voice_client.is_connected() and ctx.author.voice.channel:
                    await ctx.invoke(self.join, ctx, channel=ctx.author.voice.channel)
                    if not ctx.voice_client.is_connected():
                        player.idle = True
                        await ctx.send(get_text('play_error'))
                        return

                if not ctx.voice_client.is_playing():
                    await player.play()

            if isinstance(song, list):

                count = len(song)
                first = song.pop(0)

                try:
                    player.add_song_nowait(first)
                except QueueFull:
                    await ctx.send(f"{get_text('queue_full')} (0/{len(song) + 1})")
                    return
                await start_playing()

                not_added = await player.add_songs(song)
                if len(not_added) > 0:
                    # todo napsat kolik bylo přidáno a kolik ne (field v embed)
                    await ctx.send(f"{get_text('queue_full')} ({len(song)}/{len(not_added)})")
                    return
                await ctx.send(f"{get_text('added_to_queue')}: {count - len(song)}")  # todo embed

            else:
                try:
                    player.add_song_nowait(song)
                except QueueFull:
                    await ctx.send(get_text("queue_full"))
                    return
                await ctx.send(get_text("added_to_queue"))  # todo embed
                await start_playing()

        print("ended")

    @commands.command(name='skip', aliases=['s'])
    @commands.guild_only()
    async def skip(self, ctx, count: typing.Optional[int] = 1):
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
    def format_song_details(song: Song, return_tuple: bool = False) -> typing.Union[tuple[str, str], str]:
        if not song:
            raise ValueError("song can't be None")
        title = song.details['title']
        duration = song.details['duration']
        if return_tuple:
              return f"{title if title else '<NaN>'}", \
                     f"[{str(datetime.timedelta(seconds=duration)) if duration > 0 else '<NaN>'}]"

        return f"{title if title else '<NaN>'}" \
               f" [{str(datetime.timedelta(seconds=duration)) if duration > 0 else '<NaN>'}]"

    @commands.command(name='nowplaying', aliases=['np'])
    @commands.guild_only()
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
    @commands.guild_only()
    async def queue(self, ctx, page: typing.Optional[int] = 1):
        try:
            player = self.players[str(ctx.guild.id)]

        except KeyError:
            await ctx.send(get_text("not_playing_error"))
            return

        await player.lock.acquire()
        try:
            queue = await player.current_queue()
            # embeds = [Embed(color=Color.red())]
            # embed = embeds[0]
            # embeds_count = 0
            # if player.now_playing:
            #     embed.add_field(name=get_text("now_playing"),
            #                     value=YoutubeMusic.format_song_details(player.now_playing),
            #                     inline=False)
            #
            # index = 0
            # # sb = "Wow, such empty"
            # sb = get_text('empty')
            # if len(queue) > 0:
            #     index += 1
            #     first = f"{index}. {YoutubeMusic.format_song_details(queue.popleft())}"
            # else:
            #     first = None
            #
            # if first:
            #     sb = first
            #
            # for song in queue:
            #     index += 1
            #     embed.add_field(name="\u200b", value=f"\n{index}. {YoutubeMusic.format_song_details(song)}",
            #                     inline=False)
            #
            #     if index % 20 == 0:
            #         embeds.append(Embed(color=Color.red()))
            #         embeds_count += 1
            #         embed = embeds[embeds_count]
            #
            #     if index == 20:
            #         embed.insert_field_at(index=1,
            #                               name=f"{get_text('current_queue')} [{(len(queue) + 1)}] {get_text('song')}:",
            #                               value=sb)
            #
            # if index < 20:
            #     embed.insert_field_at(index=1, name=f"{get_text('in_queue (%s)')}"
            #                                         % (len(queue) + (1 if first else 0)),
            #                           value=sb)
            #
            # for e in embeds:
            #     await ctx.send(embed=e)
            pages = int(math.ceil(len(queue) / float(PAGE_SIZE)))
            pages = 0 if pages == 0 else pages
            if page != 1 and (page > pages or page < 1):
                await ctx.send(get_text("no_page_error") + f" ``{page}``")
                return

            embed = Embed(color=0xff0000)

            index = page * PAGE_SIZE - PAGE_SIZE

            if page == pages:
                n = page * PAGE_SIZE - 0 + len(queue) % PAGE_SIZE
            else:
                n = page * PAGE_SIZE

            page_elements = list(queue)[index:n]

            if page == 1:
                embed.add_field(name=get_text("now_playing"),
                                value=YoutubeMusic.format_song_details(player.now_playing),
                                inline=False)
            #     if len(page_elements) > 0:
            #         index += 1
            #         e = page_elements.pop(0)
            #         desc = YoutubeMusic.format_song_details(e, True)
            #         embed.add_field(name=f"{get_text('in_queue')} ({len(queue)})",
            #                         value=f"{index}. [{desc[0]}]"
            #                               f"(https://www.youtube.com/watch?v{e.details['id']}) "
            #                               f"``{desc[1]}``",
            #                         inline=False, )
            #
            #     else:
            #         embed.add_field(name=f"{get_text('in_queue')} ({len(queue)})",
            #                         value=get_text("emptiness"),
            #                         inline=False)
            #
            # for e in page_elements:
            #     index += 1
            #     desc = YoutubeMusic.format_song_details(e, True)
            #     embed.add_field(name="\u200b", value=f"{index}. [{desc[0]}]"
            #                                          f"(https://www.youtube.com/watch?v{e.details['id']}) "
            #                                          f"``{desc[1]}``",
            #                     inline=False, )
            sb = ""



            if len(page_elements)  > 0:
                for e in page_elements:
                    index += 1
                    converted = YoutubeMusic.format_song_details(e, True)

                    sb += (f"{index}. [{converted[0]}](https://www.youtube.com/watch?v{e.details['id']}) ``{converted[1]}``\n")

            else:
                sb = get_text('emptiness')

            sb += get_text('%d queue_more') % (len(queue) - index)
            embed.add_field(name=f"{get_text('in_queue')} ({len(queue)})",
                            value=sb,
                            inline=False)

            # if pages > page:
            #     embed.add_field(name='\u200b', value=f"{get_text('queue_more')} `{len(queue) - index}`")
            embed.add_field(name='\u200b', value=f"{get_text('page')} `{page}/{pages}`")
            await ctx.send(embed=embed)
        finally:
            player.lock.release()
