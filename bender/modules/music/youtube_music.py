import asyncio
import copy
import datetime
import functools
import json
import math
import os
import pathlib
import subprocess
import sys
import time
import traceback
import typing
from collections import deque
from warnings import warn

from discord import Embed, ClientException, Member, Forbidden, VoiceState
from discord.ext import commands, tasks
from discord.ext.commands import CommandInvokeError, NoPrivateMessage, CheckFailure, Context
from youtube_dl.utils import DownloadError

import bender.utils.bender_utils
from bender.modules.music import settings as player_settings
from bender.modules.music.music import MusicPlayer, AlreadyPaused, NotPaused, NoResult as YTNoResult, \
    PlayError, QueueFull, QueueEmpty, MusicSearcher
from bender.modules.music.song import Song
from bender.utils import temp as _temp, bender_utils
from bender.bot import BenderCog
from bender.utils.bender_utils import ExtensionLoadError

__all__ = ['YoutubeMusic']


def setup(bot):
    if not check_ffmpeg():
        raise ExtensionLoadError(f"{__name__} requires ffmpeg or avconv to work")

    config_path = os.path.join(_temp.get_root_path(), "youtube_music.json")
    config = YoutubeMusicConfig(config_path)

    if os.path.exists(config_path):
        try:
            config.load()
        except (OSError, ValueError):
            warn(f"Cannot read {config_path}, default configuration loaded")
        except IllegalFormat:
            warn(f"""Config in {config_path} has illegal format, 
check values or try deleting it and change values in new one

Loaded default configuration""")

    else:
        config.generate_new()
    cog = YoutubeMusic(bot, config=config)

    if config['best_quality']:
        ytdl_settings = copy.deepcopy(player_settings.YTDL_OPTIONS)
        ytdl_settings['fromat'] = "bestaudio/best"
        MusicSearcher.initialize_ytdl(ytdl_settings)
    else:
        MusicSearcher.initialize_ytdl()

    bot.add_cog(cog)


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


PAGE_SIZE = 10


def check_ffmpeg() -> bool:
    """
    Check for ffmpeg/avconv
    """
    try:
        subprocess.check_call(['ffmpeg', '-version'],
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.STDOUT)
    except Exception:
        try:
            subprocess.check_call(['avconv', '-version'],
                                  stdout=subprocess.DEVNULL,
                                  stderr=subprocess.STDOUT)
        except Exception:
            return False
    return True


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
    'max_queue_length': 100,
    'max_song_length': 7200,
    'best_quality': False,
    'max_idle_time': 180,
    'max_paused_time': 360
}


class IllegalFormat(Exception):
    pass


class YoutubeMusicConfig(dict):
    def __init__(self, path: typing.Union[str, os.PathLike]):
        if not os.path.exists(pathlib.Path(path).parent):
            raise ValueError("Path doesn't exist")
        self.path = path
        super().__init__()

    def generate_new(self):
        with open(self.path, 'w') as file:
            json.dump(DEFAULT_CONFIG, file, indent=2)

    def load(self):
        if not os.path.exists(self.path):
            raise FileNotFoundError("File doesn't exist")

        with open(self.path, 'r') as file:
            loaded = json.load(file)
        if loaded.keys() == DEFAULT_CONFIG.keys():
            for k in DEFAULT_CONFIG.keys():
                if not isinstance(loaded[k], type(DEFAULT_CONFIG[k])):
                    raise IllegalFormat()
                try:
                    if type(loaded[k]) is int and (loaded[k] > sys.maxsize or (loaded[k] < 1 and
                                                       (k != 'max_queue_length' and loaded[k] != -1))):
                        raise IllegalFormat()
                except OverflowError:
                    raise IllegalFormat()
            self.clear()
            self.update(loaded)
        else:
            raise IllegalFormat()


class YoutubeMusic(BenderCog, name="Youtube Music", description="cog_youtubemusic_description"):
    def __init__(self, bot, **kwargs):
        self.players = {}
        self.join = None
        self.garbage_collector.start()

        if kwargs:
            if 'config' in kwargs.keys():
                self.config = kwargs.pop('config')
            else:
                self.config = dict()
            for key in DEFAULT_CONFIG:
                if key in kwargs.keys():
                    self.config[key] = kwargs.pop(key)
                elif key not in self.config:
                    self.config[key] = DEFAULT_CONFIG[key]
            if kwargs:
                raise ValueError(f"Unexpected keyword arguments {kwargs}")

        else:
            self.config = copy.deepcopy(DEFAULT_CONFIG)
        super().__init__(bot)

    def cog_unload(self):
        self.garbage_collector.cancel()

    async def cog_command_error(self, ctx: Context, error):
        if isinstance(error, CommandInvokeError):
            error = error.__cause__

        if isinstance(error, DownloadError) or isinstance(error, PlayError):
            await ctx.send(self.get_text("track_stacked", await self.get_language(ctx)))
        elif isinstance(error, YTNoResult):
            await ctx.send(self.get_text("not_found_error", await self.get_language(ctx)))

        elif isinstance(error, NotInSameChannel):
            await ctx.send(self.get_text("channel_not_match_error", await self.get_language(ctx)))
        elif isinstance(error, BotNotConnected):
            await ctx.send(self.get_text("bot_not_connected_error", await self.get_language(ctx)))
        elif isinstance(error, UserNotConnected):
            await ctx.send(self.get_text("user_not_connected_error", await self.get_language(ctx)))
        elif await bender.utils.bender_utils.on_command_error(ctx, error):
            try:
                await ctx.send(self.get_text("unexpected_error", await self.get_language(ctx)))
            except Forbidden:
                pass
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    @commands.Cog.listener()
    async def on_ready(self):
        self.join = self.bot.get_command('join')

        if not self.join:
            message = f"Can't load cog {self.__class__.__name__} because it requires join command from " \
                      f"VoiceClientCommands "
            # raise BenderModuleError(message)
            print(message, file=sys.stderr)
            self.bot.remove_cog(self.qualified_name)

        if not bender.modules.music.music.MusicSearcher.initialized():
            print(f"{bender.modules.music.music.MusicSearcher.__name__} is not initialized -> cannot play from youtube",
                  file=sys.stderr)

    def is_player(self, arg: typing.Union[Context, str]) -> bool:
        if isinstance(arg, Context):
            return arg.guild.id in self.players.keys() and self.players[arg.guild.id] is not None

        elif isinstance(arg, int):
            return arg in self.players.keys() and self.players[arg] is not None

        else:
            raise TypeError(f"arg must be {int.__name__} or {Context.__name__} "
                            f"and not {arg.__class__.__name__}")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState):
        if member.id == self.bot.user.id and before.channel and after.channel \
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
            if player.voice_client and player.voice_client.channel and player.voice_client.is_playing() and \
                    len(player.voice_client.channel.members) > 1:
                player.last_used = int(time.time())
                continue
            if (not player.voice_client.is_paused() and t - player.last_used > self.config['max_idle_time']) \
                    or t - player.last_used > self.config['max_paused_time']:
                if player.voice_client.is_playing():
                    player.voice_client.stop()
                if player.voice_client.is_connected():
                    await player.voice_client.disconnect()
                    player.clear()
                del self.players[key]

        del keys
        for voice_client in self.bot.voice_clients:
            if not self.is_player(voice_client.guild.id):
                await asyncio.sleep(5)
                if not self.is_player(voice_client.guild.id):
                    try:
                        await voice_client.disconnect()
                    except Exception:
                        pass

    def can_play(self, ctx: Context) -> bool:
        return self.is_player(ctx) and ctx.voice_client.is_connected()

    def is_playing(self, ctx: Context) -> bool:
        return self.is_player(ctx) and ctx.voice_client.is_playing()

    def is_paused(self, ctx: Context) -> bool:
        return self.is_player(ctx) and ctx.voice_client.is_paused()

    def cog_check(self, ctx: Context):
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
    async def prepare_embed(ctx: Context, song: Song, embed: Embed = Embed()) -> Embed:
        bot = ctx.bot
        if song.thumbnail and len(song.thumbnail) > 0:
            embed.set_thumbnail(url=song.thumbnail[1]) if len(song.thumbnail) >= 1 else song.thumbnail[0]
        lang = await bot.get_language(ctx)
        embed.add_field(name=bot.get_text("title", lang),
                        value=f"[{song.details['title'] if song.details['title'] else 'NaN'}]"
                              f"(https://www.youtube.com/watch?v={song.details['id']})", inline=False)
        embed.add_field(name=bot.get_text("channel", lang),
                        value=song.details['uploader'] if song.details['uploader'] else 'NaN')
        embed.add_field(name=bot.get_text("song_duration", lang),
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

    @commands.command(name="play", aliases=["p"], description="command_play_description",
                      usage="command_play_usage")
    @commands.check(bender_utils.can_join_speak)
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.guild)
    async def play(self, ctx: Context, *, what: str):
        # check if in voice channel, connect to some if not
        lang = await self.get_language(ctx)
        if not ctx.voice_client or not ctx.voice_client.is_connected():
            if ctx.author.voice and ctx.author.voice.channel:
                try:
                    await asyncio.wait_for(ctx.invoke(self.join, channel=ctx.author.voice.channel), timeout=10)
                except asyncio.TimeoutError:
                    await ctx.send(self.get_text("unknown_join_error", lang))
                    return
            else:
                raise UserNotConnected()

        # check if music player for that guild exist and get it or create new player
        if ctx.guild.id in self.players.keys():
            player: MusicPlayer = self.players[ctx.guild.id]
        else:
            self.players[ctx.guild.id] = MusicPlayer(ctx.voice_client,
                                                     deque(maxlen=self.config['max_queue_length']
                                                     if self.config['max_queue_length'] > 0 else None))
            player: MusicPlayer = self.players[ctx.guild.id]

        async with player.lock:
            if ctx.voice_client and ctx.voice_client.is_connected():
                if ctx.author.voice and ctx.author.voice.channel \
                        and ctx.voice_client.channel.id != ctx.author.voice.channel.id:
                    await ctx.send(self.get_text("playing_error_different_channel", lang))
                    return
            else:
                await ctx.send(self.get_text("user_not_connected_error", lang))
                return
            # find song

            message = await ctx.send(self.get_text("searching", lang))

            loop = asyncio.get_running_loop()

            task = loop.run_in_executor(None, functools.partial(bender.modules.music.music.MusicSearcher.search_song,
                                                                what))

            try:
                song = await asyncio.wait_for(task, timeout=None)
            except Exception:
                raise
            if not song:
                await ctx.send(self.get_text("not_found_error", lang))

            if message and message.channel:
                await message.edit(content=self.get_text("found", lang))
            else:
                await ctx.send()

            # check if song isn't too long
            def check_too_long(song_to_check: Song) -> bool:
                if song_to_check.details['duration'] > 0 and \
                        song_to_check.details['duration'] > self.config['max_song_length']:
                    return True
                return False

            if isinstance(song, Song):
                if check_too_long(song):
                    await ctx.send(
                        self.get_text('%s error_too_long', lang) % f"``{YoutubeMusic.format_song_details(song)}``")
                    return
            elif isinstance(song, list):
                for s in song:
                    if check_too_long(s):
                        await ctx.send(
                            self.get_text('%s error_too_long', lang) % f"``{YoutubeMusic.format_song_details(s)}``")
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
                        await ctx.send(self.get_text('play_error', lang))
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
                    await ctx.send(self.get_text('%s queue_full', lang) % f"``(0 / {(len(song) + 1)}``")
                    return
                await start_playing()

                not_added = await player.add_songs(song)
                if len(not_added) > 0:
                    await ctx.send(self.get_text('%s queue_full', lang) % f"``{len(song)}/{len(not_added)}``")
                    return
                await ctx.send(self.get_text('%s added_to_queue', lang) % f"``{count}``")

            else:
                will_play = False
                if not player.now_playing:
                    will_play = True
                try:
                    player.add_song(song)
                except QueueFull:
                    await ctx.send(self.get_text("queue_full", lang))
                    return
                await start_playing()

                embed = await YoutubeMusic.prepare_embed(ctx, song, embed)
                embed.add_field(name=self.get_text("position", lang),
                                value=self.get_text("now_playing", lang) if will_play else str(len(player)) + '.')

                await ctx.send(embed=embed)

    @commands.command(name='skip', aliases=['s'], description="command_skip_description",
                      usage="command_skip_usage")
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
                    await ctx.send(self.get_text("queue_size_error", await self.get_language(ctx)))

                    while not player.queue_empty():
                        try:
                            player.remove()
                        except QueueEmpty:
                            break
                    try:
                        ctx.voice_client.stop()
                    except ClientException:
                        pass
                await ctx.send(self.get_text('%s skip', await self.get_language(ctx)) % f"``{qsize - player.qsize()}``")
        else:
            await ctx.send("not_playing_error")
            return

    @commands.command(name='remove', aliases=['rm'], description="command_remove_description",
                      usage="command_remove_usage")
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def remove(self, ctx: Context, position: int, *,
                     error: typing.Optional[str] = None):
        lang = await self.get_language(ctx)
        if error:
            await ctx.send(self.get_text("%s no_page_error", lang) % f"``{position} {error}``")
            return
        if self.is_playing(ctx) or self.is_paused(ctx):
            player = self.players[ctx.guild.id]
            if position < 1 or position > len(player):
                await ctx.send(self.get_text("position_error", lang))
                return
            else:
                async with player.lock:
                    song_title = player.seek(position - 1).details['title']
                    try:
                        player.remove_by_index(position)
                    except Exception:
                        await ctx.send(self.get_text("unknown_remove_error", lang))
                        raise
                    await ctx.send(self.get_text("%s removed", lang) % f"``{song_title}``")

    @commands.command(name='nowplaying', aliases=['np'], description="command_nowplaying_description",
                      usage="")
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def nowplaying(self, ctx):
        lang = await self.get_language(ctx)
        if self.is_playing(ctx) or self.is_paused(ctx):
            player = self.players[ctx.guild.id]
        else:
            await ctx.send(self.get_text("not_playing_error", lang))
            return
        if player.now_playing:
            song = player.now_playing
            embed = Embed(color=0x00ff00 if player.voice_client.is_playing() else 0xff0000)
            # embed.set_author(name=song.details['uploader'] if song.details['uploader'] else 'NaN')

            # embed.add_field(name=song.details['title'] if song.details['title'] else 'NaN',
            #                 value=f"https://www.youtube.com/watch?v={song.details['id']}\n["
            #                       + str((datetime.timedelta(seconds=song.details['duration'])) if
            #                             song.details['duration'] > 0 else '<NaN>') + "]", inline=False)
            embed.title = self.get_text("now_playing", lang)
            embed = await YoutubeMusic.prepare_embed(ctx, song, embed)
            embed.add_field(name=self.get_text("ends_in", lang),
                            value=(str(datetime.timedelta(
                                seconds=song.details['duration'] - (int(time.time()) - player.started))
                            ) if song.details['duration']
                                   else 'NaN')
                            if not player.voice_client.is_paused()
                            else self.get_text("paused", lang))

            await ctx.send(embed=embed)
            return
        else:
            await ctx.send(self.get_text("unknown_playing_error", lang))

    @commands.command(name='queue', aliases=['q'], description="command_queue_description",
                      usage="command_queue_usage")
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def queue(self, ctx, page: typing.Optional[int] = None, *, not_page: typing.Optional[str] = None):
        lang = await self.get_language(ctx)
        if not_page:
            await ctx.send(self.get_text("%s no_page_error",
                                         await self.get_language(ctx)) % f"``{page if page else '' + not_page}``")
            return
        if not page:
            page = 1
        if self.is_playing(ctx):
            player = self.players[ctx.guild.id]
        else:
            await ctx.send(self.get_text("not_playing_error", lang))
            return

        queue = player.current_queue()
        pages = int(math.ceil(len(queue) / float(PAGE_SIZE)))
        pages = 1 if pages == 0 else pages
        if page != 1 and (page > pages or page < 1):
            await ctx.send(self.get_text("%s no_page_error", lang) % f"``{page}``")
            return

        embed = Embed(color=0xff0000)
        embed.title = self.get_text('queue', lang)
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
            embed.add_field(name=self.get_text("now_playing", lang),
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
            sb = self.get_text('emptiness', lang)
        if len(queue) > index:
            sb += self.get_text('%d queue_more', lang) % f"``{(len(queue) - index)}``"
        embed.add_field(name=f"{self.get_text('%s in_queue', lang)}" % len(queue),
                        value=sb,
                        inline=False)

        embed.set_footer(text=self.get_text('%s page', lang) % f"{page}/{pages}")
        await ctx.send(embed=embed)

    @commands.command(name='pause', description="command_pause_description",
                      usage="")
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def pause(self, ctx: Context):
        lang = await self.get_language(ctx)
        if self.is_playing(ctx):
            player = self.players[ctx.guild.id]
            try:
                player.pause()
                await ctx.send(self.get_text("paused", lang))
            except AlreadyPaused:
                await ctx.send(self.get_text("already_paused_error", lang))
                return
        else:
            await ctx.send(self.get_text("not_playing_error", lang))
            return
        pass

    @commands.command(name='resume', description="command_resume_description",
                      usage="")
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def resume(self, ctx: Context):
        lang = await self.get_language(ctx)
        if self.is_paused(ctx):
            player = self.players[ctx.guild.id]
            try:
                player.resume()
                await ctx.send(self.get_text("resumed", lang))
            except NotPaused:
                await ctx.send(self.get_text("not_paused_error", lang))
                return
        else:
            await ctx.send(self.get_text("not_playing_error", lang))
            return
        pass

    @commands.command(name='loop', description="command_loop_description",
                      usage="")
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def loop(self, ctx: Context):
        lang = await self.get_language(ctx)
        if self.is_player(ctx) and ctx.voice_client.is_connected():
            player = self.players[ctx.guild.id]
            player.looped = False if player.looped else True
            if player.looped:
                await ctx.send(self.get_text("loop_on", lang))
            else:
                await ctx.send(self.get_text("loop_off", lang))
        else:
            await ctx.send(self.get_text("not_playing", lang))
