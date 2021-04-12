from __future__ import annotations

import asyncio
import functools
from asyncio import AbstractEventLoop, get_running_loop, QueueFull, QueueEmpty
from concurrent.futures import Executor

from discord import VoiceClient
from youtube_dl import YoutubeDL

from bender.modules.audio import settings
from bender.utils.queue import IndexAsyncQueue as Queue
from song import *

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
        self.now_playing: Song = None
        pass

    def add_song(self, item: Song):
        """Add song to player queue
        Raises
        -------
        QueueEmpty
            Queue of player is full"""
        self._queue.put_nowait(item)

    def add_songs(self, songs: [Song]):
        """Add all songs from array to player queue

        Raises
        -------
        QueueEmpty
            Queue of player is empty
        """
        for song in songs:
            self.add_song(song)

    def get_song(self):
        """Return and remove song from player queue
        Raises
        -------
        QueueEmpty
            Queue of player is empty
        """
        return self._queue.get_nowait()

    def get_now_playing(self) -> Song:
        """Returns now_playing

        Returns
        --------
        :class: Song
            Object of now playing audio

        Raises
        -------
        QueueEmpty
            Queue of player is empty
        """
        if self.now_playing:
            return self.now_playing
        else:
            raise NotPlaying

    def get_next(self) -> Song:
        """
        Get song from queue and prepare song after

        Returns
        --------
        :class: Song
            Next song in queue
        """
        next_song = self.get_song()
        self._queue.get_by_index(0).prepare_to_go()
        return next_song

    async def get_next_async(self):
        """
        Get song from queue and prepare song after
        Asyncio friendly

        Returns
        --------
        :class: Song
            Next song in queue
        """
        next_song = self.get_song()
        await self._queue.get_by_index(0).prepare_to_go_async()
        return next_song

    async def play(self, song: Song):
        if not self.voice_client:
            raise ValueError("voice_client can't be Null")
        elif not self.voice_client.is_connected():
            raise VoiceClientError("Not connected")
        elif self.voice_client.is_playing():
            raise AlreadyPlaying

        def play_next():
            self.voice_client.play(Song.source, after = play_next)
            self.now_playing = song

    async def play_next(self):
        await self.play(self.get_next().source)


class NotPlaying(Exception):
    """Raised by :class:`MusicPlayer.get_now_playing()` when no song playing"""
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


class MusicSearcher:
    """
    Search audio on youtube using youtube-dl
    """
    _youtube_dl = YoutubeDL(settings.YTDL_OPTIONS)

    @staticmethod
    def search_song(text: str, retry: int = 2) -> Song / [Song]:
        """
        Search for song or playlist from given url or keyword
        Returns one Song() or list of Song()
        Raise NoResult() for no result
        
        retry - How many should youtube_dl retry when first attempt fail 
        """

        def search(text: str):
            if text.startswith("https://") and (text.startswith("https://youtu.be/") or "youtube.com" in text):
                s = MusicSearcher._youtube_dl.extract_info(text, download=False)
                print(str(s))
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
                    s = MusicSearcher._youtube_dl.extract_info(f"ytsearch1:{text}", download=False)['entries'][0]

                except IndexError:
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
                result.append(Song(SongDetails(entry['id'], entry['title'], float(entry['duration']))))

            return result

        return Song(SongDetails(result['id'], result['title'], result['duration']))

    @staticmethod
    async def search_song_async(text: str, loop: AbstractEventLoop = None,
                                executor: Executor = None) -> Song / [Song]:
        """
        Execute MusicSearcher.search_song() with asyncio executor
        """
        if not loop:
            loop = get_running_loop()
        return await loop.run_in_executor(executor, functools.partial(MusicSearcher.search_song, text))
        pass

    pass

