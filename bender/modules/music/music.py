from __future__ import annotations

import copy
import sys
import time
import traceback
from asyncio import get_running_loop, run_coroutine_threadsafe, wait_for, Lock
from collections import deque
from typing import Union

from discord import VoiceClient
from youtube_dl import YoutubeDL

from bender.modules.music import settings
from bender.modules.music.song import Song, SongDetails

__all__ = ['MusicPlayer', 'MusicSearcher', 'NotPlaying', 'NotPaused', 'AlreadyPaused', 'AlreadyPlaying', 'NoSongToPlay',
           'NoResult', 'QueueFull', 'QueueEmpty', 'PlayError']

DEFAULT_PLAYER_CONFIG = {
    'YTDL_OPTIONS': copy.deepcopy(settings.YTDL_OPTIONS),
    'FFMPEG_OPTIONS': copy.deepcopy(settings.FFMPEG_OPTIONS)
}


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


class PlayError(Exception):
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
    __doc__ = """
    Object representing music player

    Attributes
    -----------
    voice_client: :class: discord.voice_client
        Voice client of bot in chosen guild

    _queue: :class: asyncio.queues.Queue
        Queue for Song objects which will be played

    now_playing: :class: Song
        Holds now playing song

    lock : asyncio.Lock
    
    started : float, None
        Time when player started playing. Is None when nothing is playing.

    """

    # todo max len
    def __init__(self, voice_client: VoiceClient, queue: deque = deque()):
        if not isinstance(voice_client, VoiceClient):
            raise TypeError(f"voice_client can't be {voice_client.__class__.__name__}")
        if not isinstance(queue, deque):
            raise TypeError(f"queue can't be {queue.__class__.__name__}")
        self.voice_client = voice_client
        self._queue = queue
        self.now_playing = None
        self.lock = Lock()
        self.last_used = int(time.time())
        self.looped = False
        self.started = None

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
            raise TypeError(f"Accept only {Song.__name__} and not {item.__class__.__name__}")
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

        TypeError
            Variable in songs isn't :class: Song
        """



        if self._queue.maxlen and len(songs) + len(self._queue) > self._queue.maxlen:
            self.add_song(songs[:(self._queue.maxlen - len(self._queue))])
            songs = songs[(self._queue.maxlen - len(self._queue)):]
        else:
            self._queue.extend(songs)
            songs = []
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
            raise TypeError("voice_client can't be Null")
        elif not self.voice_client.is_connected():
            raise VoiceClientError("Not connected")
        elif self.voice_client.is_playing():
            raise AlreadyPlaying

        loop = get_running_loop()

        song = await self.get_next()

        if not song:
            song: None
            print(f"{str(self)} finished job!")

            return
        song: Song

        def restart_play(error):
            self.started = None

            # https://discordpy.readthedocs.io/en/stable/faq.html#how-do-i-pass-a-coroutine-to-the-player-s-after-function
            if self.looped:
                song.source = None
                self.add_song(song)

            self.now_playing = None
            if error:
                print(f'Ignoring exception in method music.MusicPlayer.play.restart_play in  object'
                      f' {str(self.__hash__())}', file=sys.stderr)
                traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

            fut = run_coroutine_threadsafe(self.play(), loop)
            try:
                fut.result()
            except TimeoutError:
                # traceback.print_exc()

                return
            except VoiceClientError:
                print("<INFO> Bot was kicked or lost connection to the channel")

        if not song.source:
            await wait_for(song.prepare_to_go(), timeout=None)
        try:
            self.voice_client.play(song.source, after=restart_play)
            self.started = int(time.time())
        except Exception:
            await wait_for(song.prepare_to_go(), timeout=None)
            try:
                self.voice_client.play(song.source, after=restart_play)
                self.started = int(time.time())
            except Exception:
                raise PlayError()
        self.now_playing = song

    def remove(self, count: int = 1, return_removed: bool = False) -> Union[None, list]:

        result = None
        if count == 0:
            return
        if return_removed:
            result = list(self._queue[:count])
        self._queue = deque(list(self._queue)[:count])
        return result

    def remove_by_index(self, index: int) -> None:
        """
        Remove object from queue by given index

        Parameters
        ----------
        index : int
            Position of object in queue, which should be removed

        Raises
        ------
        IndexError
            Raised when index is out of range
        """
        try:
            del self._queue[index - 1]
        except Exception:
            raise

    def queue_empty(self) -> bool:
        """
        Return if queue is empty

        Returns
        -------
        bool
            Returns True when queue is empty otherwise returns False
        """
        return len(self._queue) == 0

    def qsize(self) -> int:
        """
        Return current size of queue

        Returns
        -------
        int
            Current size of queue
        """
        return len(self._queue)

    def current_queue(self) -> list:
        """
        Return copy of queue of player as list

        Returns
        -------
        list
            Copy of player queue
        """
        return list(self._queue)

    def pause(self) -> None:
        """
        Pause player or raise exception

        Raises
        ------
        AlreadyPaused
            Raised when trying to pause paused player
        NotPlaying
            Raised when player isn't playing
        """
        if not self.voice_client.is_playing():
            raise NotPlaying()
        if self.voice_client.is_paused():
            raise AlreadyPaused()

        self.voice_client.pause()

    def resume(self) -> None:
        """
        Resume player or raise NotPaused

        Raises
        ------
        NotPaused
            Raised when trying to unpause not paused player

        """
        if not self.voice_client.is_paused():
            raise NotPaused()

        self.voice_client.resume()

    def seek(self, index: int) -> Song:
        """
        Returns object on given position in queue of player

        Parameters
        ----------
        index : int
            Position of object in queue (starting with 0)

        Returns
        -------
        Song
            Song object on given position in self._queue

        Raises
        ------
        IndexError
            Raised when index is out of range
        """
        try:
            return self._queue[index]
        except Exception:
            raise

    def clear(self) -> None:
        """
        Clear the queue
        """
        self._queue.clear()


class MusicSearcher:
    """
    Search audio on youtube using youtube-dl
    """

    _youtube_dl = None

    @staticmethod
    def initialized():
        return MusicSearcher._youtube_dl is not None

    @staticmethod
    def initialize_ytdl(options: dict = settings.YTDL_OPTIONS):

        MusicSearcher._youtube_dl = YoutubeDL(options)

    @staticmethod
    def search_song(text: str, retry: int = 2) -> Union[Song, list[Song]]:
        """
        Search for song or playlist from given url or keyword
        Returns one Song() or list of Song()

        Attributes
        ----------
        retry - How many should youtube_dl retry when first attempt fail

        Raises
        -------
        NoResult()
            for no result
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
                except Exception:
                    return None
                return s

        result = search(text)
        while retry > 0 and result is None:
            result = search(text)
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
