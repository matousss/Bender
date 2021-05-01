from __future__ import annotations

import asyncio
import copy
import datetime
import functools
import logging
import math
import sys
import time
import traceback
import typing
from warnings import warn

from discord import Embed, ClientException, Member, Forbidden, VoiceState
from discord.ext import commands, tasks
from discord.ext.commands import CommandInvokeError, NoPrivateMessage, CheckFailure

import bender.utils.bender_utils
from bender.modules.music.music import MusicPlayer, AlreadyPaused, NotPaused, NoResult as YTNoResult, \
    PlayError, QueueFull, QueueEmpty
from bender.modules.music.song import Song
from bender.utils.bender_utils import BenderModuleError, Checks

# todo config
MAX_SONG_DURATION = 7200

is_youtube_dl = True
try:
    from youtube_dl import DownloadError
except Exception:
    is_youtube_dl = False

__all__ = ['YoutubeMusic']
logger = logging.getLogger('bender')

get_text = bender.utils.message_handler.get_text

PAGE_SIZE = 10


class BotNotConnected(CheckFailure):
    def __init__(self, message=None):
        super().__init__(message or 'Bot must be connected to voice channel to use this command.')

    pass


class UserNotConnected(CheckFailure):
    def __init__(self, message=None):
        super().__init__(message or 'You must be connected to voice channel to use this command.')

    pass


class NotInSameChannel(CheckFailure):
    def __init__(self, message=None):
        super().__init__(message or 'You must be in same channel as bot to use this command.')

    pass


DEFAULT_CONFIG = {
    'ffmpeg_avconv_path': None,
    'max_queue_size': 20,
    'max_song_length': 7200,
    'best_quality': False,
    'max_idle_time': 180,
    'max_paused_time': 360
}


@bender.utils.bender_utils.bender_module
class YoutubeMusic(commands.Cog, name="Youtube Music", description=get_text("cog_youtubemusic_description")):
    def __init__(self, bot: commands.Bot):
        if not Checks.check_ffmpeg():
            raise BenderModuleError(f"{self.__class__.__name__} requires ffmpeg or avconv to work")
        if not is_youtube_dl:
            raise BenderModuleError(f"{self.__class__.__name__} requires youtube_dl to work")
        self.BOT: commands.Bot = bot
        self.players = {}
        self.join = None
        self.garbage_collector.start()
        self.config = copy.deepcopy(DEFAULT_CONFIG)
        self.player_config = copy.deepcopy(bender.modules.music.music.DEFAULT_PLAYER_CONFIG)

        print(f"Initialized {str(__name__)}")

    def set_config(self, **kwargs):
        for key in kwargs.keys():
            if key in self.config:
                self.config[key] = kwargs[key]
            else:
                raise ValueError("Unexpected keyword argument: %s" % key)

    def set_player_config(self, **kwargs):
        for key in kwargs.keys():
            if key in self.config:
                self.player_config[key] = kwargs[key]
            else:
                raise ValueError("Unexpected keyword argument: %s" % key)

    def cog_unload(self):
        self.garbage_collector.cancel()

    async def cog_command_error(self, ctx: commands.Context, error):
        if isinstance(error, CommandInvokeError):
            error = error.__cause__

        if isinstance(error, DownloadError) or isinstance(error, PlayError):
            await ctx.send(get_text("track_stacked"))
        elif isinstance(error, YTNoResult):
            await ctx.send(get_text("no_result"))

        elif isinstance(error, NotInSameChannel):
            await ctx.send(get_text("channel_not_match_error"))
        elif isinstance(error, BotNotConnected):
            await ctx.send(get_text("bot_not_connected_error"))
        elif isinstance(error, UserNotConnected):
            await ctx.send(get_text("user_not_connected_error"))
        elif await bender.utils.bender_utils.on_command_error(ctx, error):
            try:
                await ctx.send(get_text("unexpected_error"))
            except Forbidden:
                pass
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    @commands.Cog.listener()
    async def on_ready(self):
        bender.modules.music.music.MusicSearcher.initialize_ytdl(self.player_config['YTDL_OPTIONS'])

        self.join = self.BOT.get_command('join')

        if not self.join:
            message = f"Can't load cog {self.__class__.__name__} because it requires join command from " \
                      f"VoiceClientCommands "
            # raise BenderModuleError(message)
            warn(message)
            self.BOT.remove_cog(self.qualified_name)

        if not bender.modules.music.music.MusicSearcher.initialized():
            warn(f"{bender.modules.music.music.MusicSearcher.__name__} is not initialized")

    def is_player(self, arg: typing.Union[commands.Context, str]) -> bool:
        if isinstance(arg, commands.Context):
            return arg.guild.id in self.players.keys() and self.players[arg.guild.id] is not None

        elif isinstance(arg, int):
            return arg in self.players.keys() and self.players[arg] is not None

        else:
            raise TypeError(f"arg must be {int.__name__} or {commands.Context.__name__} "
                             f"and not {arg.__class__.__name__}")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState):
        if member.id == self.BOT.user.id and before.channel and after.channel \
                and before.channel.id != after.channel.id:
            if self.is_player(member.guild.id):
                player = self.players[member.guild.id]
                player.voice_client = member.guild.voice_client

    @tasks.loop(minutes=1)
    async def garbage_collector(self):
        t = int(time.time())
        keys = list(self.players.keys())
        for key in keys:
            player = self.players[key]
            if player.voice_client.is_playing() and len(player.voice_client.channel.members) > 1:
                player.last_used = int(time.time())
                continue
            if (not player.voice_client.is_paused() and t - player.last_used > 120) or t - player.last_used > 300:
                if player.voice_client.is_connected():
                    await player.voice_client.disconnect()
                    player.clear()
                del self.players[key]

        del keys
        for voice_client in self.BOT.voice_clients:
            if not self.is_player(voice_client.guild.id):
                await asyncio.sleep(5)
                if not self.is_player(voice_client.guild.id):
                    try:
                        await voice_client.disconnect()
                    except Exception:
                        pass

    def can_play(self, ctx: commands.Context) -> bool:
        return self.is_player(ctx) and ctx.voice_client.is_connected()

    def is_playing(self, ctx: commands.Context) -> bool:
        return self.is_player(ctx) and ctx.voice_client.is_playing()

    def is_paused(self, ctx: commands.Context) -> bool:
        return self.is_player(ctx) and ctx.voice_client.is_paused()

    def cog_check(self, ctx: commands.Context):
        if ctx.guild is None:
            raise NoPrivateMessage()
        if ctx.command == self.play:
            return True
        if not ctx.voice_client or not ctx.voice_client.channel:
            raise BotNotConnected()
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise UserNotConnected()
        if ctx.voice_client.channel.id != ctx.author.voice.channel.id:
            raise NotInSameChannel()

        return True

    @staticmethod
    def prepare_embed(song: Song, embed: Embed = Embed()) -> Embed:
        if song.thumbnail and len(song.thumbnail) > 0:
            embed.set_thumbnail(url=song.thumbnail[1]) if len(song.thumbnail) >= 1 else song.thumbnail[0]
        # embed.add_field(name=song.details['title'] if song.details['title'] else 'NaN',
        #                 value=f"https://www.youtube.com/watch?v={song.details['id']}\n["
        #                       + str((datetime.timedelta(seconds=song.details['duration'])) if
        #                             song.details['duration'] > 0 else '<NaN>') + "]", inline=False)
        embed.add_field(name=get_text("title"),
                        value=f"[{song.details['title'] if song.details['title'] else 'NaN'}]"
                              f"(https://www.youtube.com/watch?v={song.details['id']})", inline=False)
        embed.add_field(name=get_text("channel"),
                        value=song.details['uploader'] if song.details['uploader'] else 'NaN')
        embed.add_field(name=get_text("song_duration"),
                        value=str((datetime.timedelta(seconds=song.details['duration'])) if
                                  song.details['duration'] > 0 else '<NaN>'))
        return embed

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

    @commands.command(name="play", aliases=["p"], description=get_text("command_play_description"),
                      help=get_text("command_play_help"), usage=f"<url/{get_text('song_title')}>")
    @commands.check(Checks.can_join_speak)
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.guild)
    async def play(self, ctx: commands.Context, *, what: str):
        # check if in voice channel, connect to some if not
        if not ctx.voice_client or not ctx.voice_client.is_connected():
            if ctx.author.voice and ctx.author.voice.channel:
                try:
                    await asyncio.wait_for(ctx.invoke(self.join, channel=ctx.author.voice.channel), timeout=10)
                except asyncio.TimeoutError:
                    await ctx.send(get_text("unknow_join_error"))
                    return
            else:
                raise UserNotConnected()

        # check if music player for that guild exist and get it or create new player
        if ctx.guild.id in self.players.keys():
            player: MusicPlayer = self.players[ctx.guild.id]
        else:
            self.players[ctx.guild.id] = MusicPlayer(ctx.voice_client)
            player: MusicPlayer = self.players[ctx.guild.id]

        async with player.lock:
            if ctx.voice_client and ctx.voice_client.is_connected():
                if ctx.author.voice.channel and ctx.voice_client.channel.id != ctx.author.voice.channel.id:
                    await ctx.send(get_text("playing_error_different_channel"))
                    return
            else:
                await ctx.send(get_text("user_not_connected"))
                return
            # find song

            message = await ctx.send(get_text("searching"))

            loop = asyncio.get_running_loop()

            task = loop.run_in_executor(None, functools.partial(bender.modules.music.music.MusicSearcher.search_song,
                                                                what))

            try:
                song = await asyncio.wait_for(task, timeout=None)
            except Exception:
                raise
            if not song:
                await ctx.send(get_text("not_found_error"))

            if message and message.channel:
                await message.edit(content=get_text("found"))
            else:
                await ctx.send()

            # check if song isn't too long
            def check_too_long(song_to_check: Song) -> bool:
                # todo settings
                if song_to_check.details['duration'] > 0 and song_to_check.details['duration'] > MAX_SONG_DURATION:
                    return True
                return False

            if isinstance(song, Song):
                if check_too_long(song):
                    await ctx.send(get_text('%s error_too_long') % f"``{YoutubeMusic.format_song_details(song)}``")
                    return
            elif isinstance(song, list):
                for s in song:
                    if check_too_long(s):
                        await ctx.send(get_text('%s error_too_long') % f"``{YoutubeMusic.format_song_details(s)}``")
                        song.remove(s)

            else:
                raise TypeError(
                    f'song must be {Song.__name__} or {list.__name__}, but instead got {song.__class__.__name__}')

            async def start_playing():
                # in case of unexpected disconnect
                if (not ctx.voice_client or not ctx.voice_client.is_connected()) and ctx.author.voice.channel:
                    try:
                        await asyncio.wait_for(ctx.invoke(self.join, channel=ctx.author.voice.channel), timeout=10)
                    except asyncio.TimeoutError:
                        player.idle = True
                        await ctx.send(get_text('play_error'))
                        return

                if not ctx.voice_client.is_playing():
                    await player.play()

            embed = Embed(color=0xff0000)
            if isinstance(song, list):

                count = len(song)
                first = song.pop(0)

                try:
                    player.add_song(first)
                except QueueFull:
                    await ctx.send(get_text('%s queue_full') % f"``(0 / {(len(song) + 1)}``")
                    return
                await start_playing()

                not_added = await player.add_songs(song)
                if len(not_added) > 0:
                    await ctx.send(get_text('%s queue_full') % f"``{len(song)}/{len(not_added)}``")
                    return
                await ctx.send(get_text('%s added_to_queue') % f"``{count}``")

            else:
                will_play = False
                if not player.now_playing:
                    will_play = True
                try:
                    player.add_song(song)
                except QueueFull:
                    await ctx.send(get_text("queue_full"))
                    return
                await start_playing()

                embed = YoutubeMusic.prepare_embed(song, embed)
                embed.add_field(name=get_text("position"),
                                value=get_text("now_playing") if will_play else str(len(player)) + '.')

                await ctx.send(embed=embed)

    @commands.command(name='skip', aliases=['s'], description=get_text("command_skip_description"),
                      help=get_text("command_skip_help"), usage=f"[{get_text('count')}]")
    @commands.cooldown(1, .5, commands.BucketType.guild)
    async def skip(self, ctx, count: typing.Optional[int] = 1):
        if self.is_playing(ctx) or self.is_paused(ctx):
            player = self.players[ctx.guild.id]
            if player.now_playing:
                a = 1
            else:
                a = 0
            qsize = player.qsize() + a
            async with player.lock:

                if count <= len(player) + a:

                    try:
                        if player.now_playing:
                            player.remove(count - 1)
                            if player.looped:
                                player.looped = False
                                ctx.voice_client.stop()
                                player.looped = True
                            else:
                                ctx.voice_client.stop()
                        else:
                            player.remove(count)

                    except QueueEmpty:
                        pass
                    except ClientException:
                        pass
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
                await ctx.send(f"{get_text('skip')} : {qsize - player.qsize()}")
        else:
            await ctx.send("not_playing_error")
            return

    @commands.command(name='remove', aliases=['rm'], description=get_text("command_remove_description"),
                      help=get_text("command_remove_help"), usage=f"<{get_text('position_in_queue')}>")
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def remove(self, ctx: commands.Context, position: int, *,
                     error: typing.Optional[str] = None):
        if error:
            await ctx.send(get_text("%s no_page_error") % f"``{position} {error}``")
            return
        if self.is_playing(ctx) or self.is_paused(ctx):
            player = self.players[ctx.guild.id]
            if position < 1 or position > len(player):
                await ctx.send(get_text("position_error"))
                return
            else:
                async with player.lock:
                    song_title = player.seek(position - 1).details['title']
                    try:
                        player.remove_by_index(position)
                    except Exception:
                        await ctx.send(get_text("unknown_remove_error"))
                        raise
                    await ctx.send(get_text("%s removed") % f"``{song_title}``")

    @commands.command(name='nowplaying', aliases=['np'], description=get_text("command_nowplaying_description"),
                      help=get_text("command_nowplaying_help"), usage="")
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def nowplaying(self, ctx):
        if self.is_playing(ctx) or self.is_paused(ctx):
            player = self.players[ctx.guild.id]
        else:
            await ctx.send("not_playing_error")
            return
        if player.now_playing:
            song = player.now_playing
            embed = Embed(color=0x00ff00 if player.voice_client.is_playing() else 0xff0000)
            # embed.set_author(name=song.details['uploader'] if song.details['uploader'] else 'NaN')

            # embed.add_field(name=song.details['title'] if song.details['title'] else 'NaN',
            #                 value=f"https://www.youtube.com/watch?v={song.details['id']}\n["
            #                       + str((datetime.timedelta(seconds=song.details['duration'])) if
            #                             song.details['duration'] > 0 else '<NaN>') + "]", inline=False)
            embed.title = get_text("now_playing")
            embed = YoutubeMusic.prepare_embed(song, embed)
            embed.add_field(name=get_text("ends_in"),
                            value=(str(datetime.timedelta(
                                seconds=song.details['duration'] - (int(time.time()) - player.started))
                            ) if song.details['duration']
                                   else 'NaN')
                            if not player.voice_client.is_paused()
                            else get_text("paused"))

            await ctx.send(embed=embed)
            return
        else:
            await ctx.send(get_text("unknow_playing_error"))

    @commands.command(name='queue', aliases=['q'], description=get_text("command_queue_description"),
                      help=get_text("command_queue_help"), usage=f"<{get_text('page')}>")
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def queue(self, ctx, page: typing.Optional[int] = None, *, not_page: typing.Optional[str] = None):
        if not_page:
            await ctx.send(get_text("no_page_error") + f" ``{page if page else '' + not_page}``")
            return
        if not page:
            page = 1
        if self.is_playing(ctx):
            player = self.players[ctx.guild.id]
        else:
            await ctx.send("not_playing_error")
            return

        queue = player.current_queue()
        pages = int(math.ceil(len(queue) / float(PAGE_SIZE)))
        pages = 1 if pages == 0 else pages
        if page != 1 and (page > pages or page < 1):
            await ctx.send(get_text("no_page_error") + f" ``{page}``")
            return

        embed = Embed(color=0xff0000)
        embed.title = get_text('queue')
        index = page * PAGE_SIZE - PAGE_SIZE

        if page == pages:
            n = page * PAGE_SIZE - 0 + len(queue) % PAGE_SIZE
        else:
            n = page * PAGE_SIZE

        page_elements = list(queue)[index:n]

        if page == 1:
            now_playing = player.now_playing
            converted = YoutubeMusic.format_song_details(now_playing, True)

            if now_playing.thumbnail and len(now_playing.thumbnail) > 0:
                embed.set_thumbnail(url=now_playing.thumbnail[1]) if len(now_playing.thumbnail) >= 1 else \
                    now_playing.thumbnail[0]
            embed.add_field(name=get_text("now_playing"),
                            value=f"[{converted[0]}](https://www.youtube.com/watch?v"
                                  f"{now_playing.details['id']}) {converted[1]}", inline=False)
        sb = ""

        if len(page_elements) > 0:
            for e in page_elements:
                index += 1
                converted = YoutubeMusic.format_song_details(e, True)

                sb += (
                    f"{index}. [{converted[0]}](https://www.youtube.com/watch?v{e.details['id']}) {converted[1]}\n")

        else:
            sb = get_text('emptiness')
        if len(queue) > index:
            sb += get_text('%d queue_more') % f"``{(len(queue) - index)}``"
        embed.add_field(name=f"{get_text('%d in_queue')}" % len(queue),
                        value=sb,
                        inline=False)

        # if pages > page:
        #     embed.add_field(name='\u200b', value=f"{get_text('queue_more')} `{len(queue) - index}`")
        # embed.add_field(name='\u200b', value=f"{get_text('page')} `{page}/{pages}`")
        embed.set_footer(text=f"{get_text('page')} {page}/{pages}")
        await ctx.send(embed=embed)

    @commands.command(name='pause', description=get_text("command_pause_description"),
                      help=get_text("command_pause_help"), usage="")
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def pause(self, ctx: commands.Context):
        if self.is_playing(ctx):
            player = self.players[ctx.guild.id]
            try:
                player.pause()
                await ctx.send(get_text("paused"))
            except AlreadyPaused:
                await ctx.send(get_text("already_paused_error"))
                return
        else:
            await ctx.send("not_playing_error")
            return
        pass

    @commands.command(name='resume', description=get_text("command_resume_description"),
                      help=get_text("command_resume_help"), usage="")
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def resume(self, ctx: commands.Context):
        if self.is_paused(ctx):
            player = self.players[ctx.guild.id]
            try:
                player.resume()
                await ctx.send(get_text("resumed"))
            except NotPaused:
                await ctx.send(get_text("not_paused_error"))
                return
        else:
            await ctx.send("not_playing_error")
            return
        pass

    @commands.command(name='loop', description=get_text("command_loop_description"),
                      help=get_text("command_loop_help"), usage="")
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def loop(self, ctx: commands.Context):
        if self.is_player(ctx) and ctx.voice_client.is_connected():
            player = self.players[ctx.guild.id]
            player.looped = False if player.looped else True
            if player.looped:
                await ctx.send(get_text("loop_on"))
            else:
                await ctx.send(get_text("loop_off"))
        else:
            await ctx.send(get_text("not_playing"))
