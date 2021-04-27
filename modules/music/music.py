from __future__ import annotations

import time
from asyncio import get_running_loop, run_coroutine_threadsafe, wait_for, Lock
from collections import deque
from typing import Union

from discord import VoiceClient
from youtube_dl import YoutubeDL, DownloadError

from . import settings
from .song import *

__all__ = ['MusicPlayer', 'MusicSearcher', 'NotPlaying', 'NotPaused', 'AlreadyPaused', 'AlreadyPlaying', 'NoSongToPlay',
           'NoResult', 'QueueFull', 'QueueEmpty']


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


class QueueFull(Exception):
    pass


class QueueEmpty(Exception):
    pass


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

    def __init__(self, voice_client: VoiceClient, queue: deque = deque()):
        if not isinstance(voice_client, VoiceClient):
            raise ValueError(f"voice_client can't be {voice_client.__class__.__name__}")
        if not isinstance(queue, deque):
            raise ValueError(f"queue can't be {queue.__class__.__name__}")
        self.voice_client = voice_client
        self._queue = queue
        self.now_playing = None
        self.lock = Lock()
        self.searcher = MusicSearcher()
        self.last_used = int(time.time())
        self.looped = False
        pass

    def __len__(self):
        """
        Returns
        --------
        int
            Number of items in queue
        """
        return len(self._queue)

    def __getattribute__(self, item):
        method = object.__getattribute__(self, item)
        if callable(method):
            self.last_used = int(time.time())

        return method

    def add_song(self, item: Song):
        """Add song to player queue
        Raises
        -------
        QueueFull
            Queue of player is full"""
        if not isinstance(item, Song):
            raise ValueError(f"Accept only {Song.__name__} and not {item.__class__.__name__}")
        if self._queue.maxlen == len(self._queue):
            raise QueueFull("Player queue is full")
        self._queue.append(item)

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
                        self.add_song(song)
                        # taks = self.add_song_nowait(song)
                        # await wait_for(task, timeout=None)

                    except QueueFull:
                        songs.insert(0, song)
                        raise
                else:
                    raise ValueError(f"Accept only {Song.__name__} and not {song.__class__.__name__}")

        finally:
            return songs

    def get_song(self) -> Song:
        if len(self._queue) == 0:
            raise QueueEmpty()
        return self._queue.popleft()

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

    async def get_next(self) -> Union[Song, None]:
        """
        Get song from queue and if queue isn't empty prepare next song in queue

        Returns
        --------
        :class: Song
            Next song in queue

        None
            None is returned when queue is empty
        """
        try:
            next_song = self.get_song()
        except QueueEmpty:
            return None
        if len(self._queue) > 0:
            after = self._queue[0]
            await after.prepare_to_go()
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
            if self.looped:
                self.add_song(song)
            if error:
                print(error)

            fut = run_coroutine_threadsafe(self.play(), loop)
            try:
                fut.result()
            except TimeoutError:
                # traceback.print_exc()

                return
            except VoiceClientError:
                print("<INFO> Bot was kicked by user or lost connection to channel")

        song = await self.get_next()

        if not song:
            print(f"{str(self)} is idle")

            return

        if not song.source:
            await wait_for(song.prepare_to_go(), timeout=None)
        try:
            self.voice_client.play(song.source, after=restart_play)
        except:
            await wait_for(song.prepare_to_go(), timeout=None)
            try:
                self.voice_client.play(song.source, after=restart_play)
            except:
                raise DownloadError()
        self.now_playing = song

    def remove(self, count: int = 1):
        for _ in range(count):
            self._queue.popleft()

    # todo remove by index

    def queue_empty(self) -> bool:
        return len(self._queue) == 0

    def qsize(self):
        return len(self._queue)

    def current_queue(self) -> list:
        return list(self._queue)

    def pause(self):
        if not self.voice_client.is_playing():
            raise NotPlaying()
        if self.voice_client.is_paused():
            raise AlreadyPaused()

        self.voice_client.pause()

    def resume(self):
        if not self.voice_client.is_paused():
            raise NotPaused()

        self.voice_client.resume()


class MusicSearcher(object):
    """
    Search audio on youtube using youtube-dl
    """

    _youtube_dl = YoutubeDL(settings.YTDL_OPTIONS)

    @staticmethod
    def search_song(text: str, retry: int = 2) -> Union[Song, list[Song]]:
        """
        Search for song or playlist from given url or keyword
        Returns one Song() or list of Song()
        Raises
        -------
        NoResult()
            for no result
        
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
                "youtube_dl didn't returned any result\nthis error can be caused by connection problems, "
                "outdated youtube_dl or invalid url")
        if 'entries' in result:
            x = result
            result = []
            for entry in x['entries']:
                # noinspection PyTypeChecker
                result.append(Song(SongDetails(entry['id'], entry['title'], float(entry['duration']))))

            return result
        return Song(SongDetails(result['id'], result['title'], result['duration'], result['uploader']))

    pass
