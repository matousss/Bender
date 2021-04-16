from __future__ import annotations

from asyncio import get_running_loop, run_coroutine_threadsafe, wait_for, create_task, QueueEmpty, \
    Lock
from asyncio.queues import QueueFull

from discord import VoiceClient
from youtube_dl import YoutubeDL

from bender.utils.queue import IndexAsyncQueue as Queue
from . import settings
from .song import *

__all__ = ['MusicPlayer', 'MusicSearcher']


class MusicPlayer():
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
        pass

    def __len__(self):
        """
        Returns
        --------
        int
            Number of items in queue
        """
        return self._queue.qsize()

    async def add_song(self, item: Song):
        """Add song to player queue
        Raises
        -------
        QueueEmpty
            Queue of player is full"""
        print("dasdkjljnsjkadjksjkdnsjn" + str(item))
        self._queue.put_nowait(item)

    async def add_songs(self, songs: type([Song])):
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
        song = None
        try:
            for _ in songs:
                song = songs.pop(0)
                if isinstance(song, Song):
                    try:
                        await self.add_song(song)
                    except QueueFull:
                        songs.insert(0, song)
                else:
                    raise ValueError(f"Accept only {Song.__name__} and not {song.__class__.__name__}")
        finally:
            return songs

    async def get_song(self):
        """
        Return and remove song from player queue

        Raises
        -------
        QueueEmpty
            Queue of player is empty
        """

        return self._queue.get_nowait()

    async def get_now_playing(self) -> Song:
        """Returns now_playing

        Returns
        --------
        :class: Song
            Object of now playing audio

        None
            Returned when nothing is playing
        """
        if self.now_playing:
            return self.now_playing
        else:
            raise NotPlaying

    # async def get_next(self) -> Song:
    #     """
    #     Get song from queue and prepare song after
    #
    #     Returns
    #     --------
    #     :class: Song
    #         Next song in queue
    #     """
    #     next_song = await self.get_song()
    #     self._queue.get_by_index(0).prepare_to_go()
    #     return next_song

    async def get_next(self) -> Song:
        """
        Get song from queue and prepare song after
        Asyncio friendly

        Returns
        --------
        :class: Song
            Next song in queue
        """

        next_song = await self.get_song()
        print(next_song)
        try:
            after = self._queue.get_by_index(0)
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
            print(error)
            coro = self.play()
            fut = run_coroutine_threadsafe(coro, loop)
            try:
                fut.result()
            except QueueEmpty:
                return

        song = await self.get_next()
        task = create_task(song.prepare_to_go())
        if not song.source:
            await wait_for(task, timeout=None)
        print("skoro to hraje")
        self.voice_client.play(song.source, after=restart_play)
        print("hnůj " + str(song))
        self.now_playing = song
        print("už hraju")

    def remove(self, count: int = 1):
        for _ in range(count):
            self._queue.get_nowait()

    def queue_empty(self) -> bool:
        return self._queue.empty()

    def qsize(self):
        return self._queue.qsize()


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
                result.append(Song(SongDetails(entry['id'], entry['title'], float(entry['duration']))))

            return result

        return Song(SongDetails(result['id'], result['title'], result['duration']))

    # async def search_song_async(self, text: str, loop: AbstractEventLoop = None,
    #                             executor: Executor = ThreadPoolExecutor()) -> Song / [Song]:
    #     """
    #     Execute MusicSearcher.search_song() with asyncio executor
    #     """
    #     await self.lock.acquire()
    #     try:
    #
    #         if not loop:
    #             loop = get_running_loop()
    #         print("zatím jedu")
    #         task = loop.run_in_executor(executor, functools.partial(self.search_song, text))
    #         return await wait_for(task, timeout=None)
    #
    #     finally:
    #         print("nejedu")
    #         self.lock.release()

    pass
