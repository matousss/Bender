from __future__ import annotations

import asyncio
import functools
from asyncio import AbstractEventLoop, get_running_loop, QueueFull
from concurrent.futures import Executor

import discord
from youtube_dl import YoutubeDL

from bender.modules.audio import settings
from bender.utils.queue import IndexAsyncQueue as Queue
from song import *

__all__ = ['MusicPlayer', 'MusicSearcher']


class MusicPlayer(object):
    def __init__(self, voice_client: discord.voice_client, queue: Queue):
        self._voice_client = voice_client
        self._queue = queue
        self.now_playing: Song = None
        pass

    def add_song(self, item: Song):
        """Add song to player queue
        Can raise asyncio.QueueFull"""
        self._queue.put_nowait(item)

    def add_songs(self, songs: [Song]):
        """Add all songs from array to player queue
        Can raise asyncio.QueueFull"""
        for song in songs:
            try:
                self.add_song(song)
            except QueueFull as e:
                raise e

    def get_song(self):
        """Return and remove song from player queue"""
        return self._queue.get_nowait()

    def get_now_playing(self) -> Song:
        """Returns now_playing or raise NotPlaying"""
        if self.now_playing:
            return self.now_playing
        else:
            raise NotPlaying

    def get_next(self):
        """Get song from queue and prepare song after"""
        next_song = self._queue.get_nowait()
        print("čabraka" + str(self._queue.get_by_index(0)))
        return next_song

    pass


class NotPlaying(Exception):
    """Raised by MusicPlayer.get_now_playing() when no song playing"""
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


async def this():
    MusicSearcher.search_song("https://www.youtube.com/playlist?list=PLfyTELTjgPDmJppx0cnnP2N0n-y0xV7x0")
    MusicSearcher.search_song("boom boom boom")
    MusicSearcher.search_song("llyiQ4I-mcQ")
    # MusicSearcher.search_song("https://www.pornhub.com/view_video.php?viewkey=ph605801aab1ef2")
    mp = MusicPlayer(None, Queue())
    MusicSearcher.search_song()
    mp.add_song(MusicSearcher.search_song("llyiQ4I-mcQ"))
    mp.add_song(MusicSearcher.search_song("https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstleyVEVO"))
    print(mp.get_next())


if __name__ == '__main__':
    print("dnmasjdjnij")
    asyncio.run(this())
