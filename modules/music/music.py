from __future__ import annotations

import traceback
from asyncio import get_running_loop, run_coroutine_threadsafe, wait_for, Lock, TimeoutError as AsyncioTimeoutError
from asyncio.queues import QueueFull
from typing import Coroutine, Union

from discord import VoiceClient
from youtube_dl import YoutubeDL

from utils.lib import Checks
from utils.queue import IndexAsyncQueue as Queue
from utils.utils import BenderModuleError
from . import settings
from .song import *

__all__ = ['MusicPlayer', 'MusicSearcher']


class MusicPlayer(object):
    """
    Object representing music player

    Attributes
    -----------
    voice_client: :class: discord.voice_client
        Voice client of bot in chosen guild

    _queue: :class: asyncio.queues.Queue
        Queue for :class: Song object which will be played

    now_playing: :class: Song
        Holds now playing song
    """

    def __init__(self, voice_client: VoiceClient, queue: Queue = Queue()):
        if not isinstance(voice_client, VoiceClient):
            raise ValueError(f"voice_client can't be {voice_client}")
        if not isinstance(queue, Queue):
            raise ValueError(f"queue can't be {queue}")
        self.voice_client = voice_client
        self._queue = queue
        self.now_playing = None
        self.lock = Lock()
        self.searcher = MusicSearcher()
        self.idle = True
        pass

    def __len__(self):
        """
        Returns
        --------
        int
            Number of items in queue
        """
        return self._queue.qsize()

    def __getattribute__(self, item):
        method = object.__getattribute__(self, item)
        if callable(method):
            if self.idle:
                self.idle = False
        return method

    def __del__(self):
        if self.voice_client and self.voice_client.is_connected():
            try:
                loop = get_running_loop()
                fut = run_coroutine_threadsafe(self.voice_client.disconnect(), loop)
            except Exception:
                traceback.print_exc()
                return

            try:
                fut.result()
            except Exception:
                traceback.print_exc()

    def add_song_nowait(self, item: Song):
        """Add song to player queue
        Raises
        -------
        QueueFull
            Queue of player is full"""
        if not isinstance(item, Song):
            raise ValueError(f"Accept only {Song.__name__} and not {item.__class__.__name__}")
        self._queue.put_nowait(item)

    async def add_songs(self, songs: list):
        """Add all songs from array to player queue

        Returns
        --------
        :class: Song
            List of :class: Song which were not added to queue because of QueueFull exception

        Raises
        -------
        QueueEmpty
            Queue of player is empty

        ValueError
            Variable in songs isn't :class: Song
        """

        try:
            while len(songs) > 0:
                song = songs.pop(0)
                if isinstance(song, Song):
                    try:
                        self.add_song_nowait(song)
                        # taks = self.add_song_nowait(song)
                        # await wait_for(task, timeout=None)

                    except QueueFull:
                        songs.insert(0, song)
                        raise
                else:
                    raise ValueError(f"Accept only {Song.__name__} and not {song.__class__.__name__}")

        finally:
            return songs

    async def get_song_nowait(self) -> Song:
        return self._queue.get_nowait()

    async def get_song(self) -> Coroutine:
        return self._queue.get()

    async def get_now_playing(self) -> Song:
        """Returns now_playing

        Returns
        --------
        :class: Song
            Object of now playing audio

        None
            Returned when nothing is playing
        """
        return self.now_playing

    async def get_next(self, timeout: float = None) -> Union[Song, None]:
        """
        Get song from queue and prepare song after

        Returns
        --------
        :class: Song
            Next song in queue

        None
            None is returned when queue is empty and timeout occurred
        """
        try:
            next_song = await wait_for(await self.get_song(), timeout=timeout)
        except AsyncioTimeoutError:
            return None
        if not self._queue.empty():
            after = await self._queue.get_by_index(0)
            await after.prepare_to_go()
        return next_song

    async def get_next_nowait(self) -> Union[Song, None]:
        """
        Get song from queue and prepare song after

        Returns
        --------
        :class: Song
            Next song in queue
        """

        next_song = await self.get_song_nowait()

        try:
            after = await self._queue.get_by_index(0)
            await after.prepare_to_go()

        except IndexError:
            pass

        return next_song

    async def play(self) -> None:
        if not self.voice_client:
            raise ValueError("voice_client can't be Null")
        elif not self.voice_client.is_connected():
            raise VoiceClientError("Not connected")
        elif self.voice_client.is_playing():
            raise AlreadyPlaying

        loop = get_running_loop()

        def restart_play(error):
            # https://discordpy.readthedocs.io/en/stable/faq.html#how-do-i-pass-a-coroutine-to-the-player-s-after-function
            if error:
                print(error)
            coro = self.play()
            fut = run_coroutine_threadsafe(coro, loop)
            try:
                fut.result()
            except TimeoutError:
                # traceback.print_exc()
                print(self.idle)
                return
            except VoiceClientError:
                print("<INFO> Bot was kicked by user or lost connection to channel")

        song = await self.get_next(timeout=30.0)
        if not song:
            self.idle = True
            print(f"{str(self)} is idle")

            return

        if not song.source:
            await wait_for(song.prepare_to_go(), timeout=None)

        self.voice_client.play(song.source, after=restart_play)

        self.now_playing = song

    def remove(self, count: int = 1):
        for _ in range(count):
            self._queue.get_nowait()

    def queue_empty(self) -> bool:
        return self._queue.empty()

    def qsize(self):
        return self._queue.qsize()

    async def current_queue(self) -> list:
        return await self._queue.get_current()

    def pause(self):
        if not self.voice_client.is_playing():
            raise AlreadyPlaying()
        if self.voice_client.is_paused():
            raise AlreadyPaused()
        try:
            self.voice_client.pause()
        except Exception:
            traceback.print_exc()

    def resume(self):
        if not self.voice_client.is_paused():
            raise NotPaused()

        try:
            self.voice_client.resume()
        except Exception:
            traceback.print_exc()


class NotPlaying(Exception):
    """Raised by :class: MusicPlayer.get_now_playing() when no song playing"""
    pass


class NotPaused(Exception):
    """Raised by MusicPlayer().resume() when isn't paused"""
    pass


class AlreadyPaused(Exception):
    """Raised by MusicPlayer().pause() when is already paused"""
    pass


class AlreadyPlaying(Exception):
    """Raised by MusicPlayer.play() when audio is already playing"""
    pass


class VoiceClientError(Exception):
    """Raised by MusicPlayer on error with voice_client"""

    def __init__(self, desc: any = None):
        self.desc = desc
        super().__init__(self, desc)


class NoSongToPlay(Exception):
    """Raised by MusicPlayer.play"""
    pass


class NoResult(Exception):
    """Raised by MusicSearcher.search_song() when no result"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

    pass


class MusicSearcher(object):
    """
    Search audio on youtube using youtube-dl
    """

    _youtube_dl = YoutubeDL(settings.YTDL_OPTIONS)

    @staticmethod
    def search_song(text: str, retry: int = 2):
        """
        Search for song or playlist from given url or keyword
        Returns one Song() or list of Song()
        Raise NoResult() for no result
        
        retry - How many should youtube_dl retry when first attempt fail 
        """

        def search(keywords: str):

            if keywords.startswith("https://") and (keywords.startswith("https://youtu.be/") or
                                                    "youtube.com" in keywords):

                s = MusicSearcher._youtube_dl.extract_info(keywords, download=False)

                if 'formats' in s:
                    convert = {'_type': 'url_transparent', 'ie_key': '', 'id': s['id'], 'url': s['id'],
                               'title': s['title'],
                               'description': s['description'], 'duration': s['duration'],
                               'view_count': s['view_count'],
                               'uploader': s['uploader']}
                    s = convert
                return s
            else:
                try:

                    s = MusicSearcher._youtube_dl.extract_info(f"ytsearch1:{keywords}", download=False)['entries'][0]

                except IndexError or TypeError:
                    return None
                return s

        result = search(text)
        while retry > 0 and result is None:
            result = search(text)
            print(f"Pokus: {retry}")
            retry -= 1

        if not result:
            raise NoResult(
                "youtube_dl didn't returned any result\nthis error can be caused by connection problems or invalid url")
        if 'entries' in result:
            x = result
            result = []
            for entry in x['entries']:
                # noinspection PyTypeChecker
                result.append(Song(SongDetails(entry['id'], entry['title'], float(entry['duration']))))

            return result

        return Song(SongDetails(result['id'], result['title'], result['duration']))

    pass
