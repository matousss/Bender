from __future__ import annotations

import functools
from asyncio import AbstractEventLoop, get_running_loop
from concurrent.futures import Executor

from discord.player import FFmpegPCMAudio
from youtube_dl import YoutubeDL

from settings import YTDL_OPTIONS
from settings import FFMPEG_OPTIONS

__all__ = ['Song', 'SongDetails']


class SongDetails(dict):
    """Object to store basic audio details"""

    def __init__(self, id: str, title: str = None, duration: float = -1):
        self['id'] = id
        self['title'] = title
        self['duration'] = duration
        super().__init__()


class Song(object):
    """Object representing youtube video"""

    def __init__(self, details: SongDetails, thumbnail: str = None, source: FFmpegPCMAudio = None):
        """
        details - instance of SongDetails containing basic info about youtube video
        thumbnail - optional url for thumbnail image
        source - optional audio source represented with FFmpegPCMAudio from discord.player
        """
        self.details = details
        self.source: FFmpegPCMAudio = source
        self.thumbnail = thumbnail
        pass

    def __str__(self):
        return str(self.details)

    def ready(self) -> bool:
        return not self.source is None

    def prepare_to_go(self) -> None:
        """Prepare song for usage on discord"""
        extracted = SongExtractor.extract_song(f"https://www.youtube.com/watch?v={self.details['id']}")
        self.source = FFmpegPCMAudio(extracted[0])
        self.thumbnail = extracted[1]
        pass

    async def prepare_to_go_async(self):
        """Prepare song for usage on discord but asyncio friendly"""
        extracted = await SongExtractor.extract_song_async(f"https://www.youtube.com/watch?v={self.details['id']}")
        self.source = FFmpegPCMAudio(extracted[0], options=FFMPEG_OPTIONS)
        self.thumbnail = extracted[1]

    pass


class SongExtractor:
    _youtube_dl = YoutubeDL(YTDL_OPTIONS)

    @staticmethod
    def extract_song(url: str) -> tuple[str, str]:
        """
        Get audio and thumbnail direct url with YoutubeDL and return it

        Parameters
        -----------
        url: :class:
            Must be in format "https://www.youtube.com/watch?v=<some_id>"
        """
        song = SongExtractor._youtube_dl.extract_info("https://www.youtube.com")
        print(str(song))
        return song['formats'][0], song['formats'][0]['thumbnails'][0]['url']

    @staticmethod
    async def extract_song_async(url: str, loop: AbstractEventLoop = None, executor: Executor = None) -> tuple[str, str]:
        """
        Execute SongExtractor.extract_song() with asyncio executor
        """
        if not loop:
            loop = get_running_loop()
        return await loop.run_in_executor(executor, functools.partial(SongExtractor.extract_song, url))
