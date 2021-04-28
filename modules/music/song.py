from __future__ import annotations

import functools
from asyncio import AbstractEventLoop, get_running_loop
from concurrent.futures import Executor
from concurrent.futures.thread import ThreadPoolExecutor

from discord.player import FFmpegPCMAudio
from youtube_dl import YoutubeDL

from .settings import FFMPEG_OPTIONS
from .settings import YTDL_OPTIONS

__all__ = ['Song', 'SongDetails']


class SongDetails(dict):
    """Object to store basic audio details"""

    def __init__(self, id: str, title: str = None, duration: float = -1, uploader: str = None):
        self['id'] = id
        self['title'] = title
        self['duration'] = duration
        self['uploader'] = uploader
        super().__init__()


class Song(object):
    """Object representing youtube video"""

    def __init__(self, details: SongDetails, thumbnail: list = None, source: FFmpegPCMAudio = None):
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

    def prepare_to_go_blocking(self) -> None:
        """
        Prepare song for usage on discord

        Raises
        ------
        youtube_dl.DownloadError
            Raised when youtube_dl cannot download specified video
        """
        extracted = SongExtractor.extract_song_blocking(f"https://www.youtube.com/watch?v={self.details['id']}")
        self.source = FFmpegPCMAudio(extracted[0])
        self.thumbnail = extracted[1]
        pass

    async def prepare_to_go(self) -> None:
        """
        Prepare song for usage on discord but uses non blocking SongExtractor.extract_song

        Raises
        ------
        youtube_dl.DownloadError
            Raised when youtube_dl cannot download specified video
        """
        extracted = await SongExtractor.extract_song(f"https://www.youtube.com/watch?v={self.details['id']}")

        self.source = FFmpegPCMAudio(extracted[0], **FFMPEG_OPTIONS)
        self.thumbnail = extracted[1]
        return

    pass


class SongExtractor:
    _youtube_dl = YoutubeDL(YTDL_OPTIONS)

    @staticmethod
    def extract_song_blocking(url: str) -> tuple[str, list]:
        """
        Get audio and thumbnail direct url with YoutubeDL and return it

        Parameters
        -----------
        url : str
            Url to youtube video
            | Must be in format: "https://www.youtube.com/watch?v=<some_id>"

        Returns
        -------
        tuple
            Tuple of str and list
            | str
                Direct url to extracted video

            | list
                List of links to thumbnails with 2 highest resolutions
        """
        song = SongExtractor._youtube_dl.extract_info(url, download=False)

        thumbnails = [None, None]
        index = 0
        for t in song['thumbnails'][-2:]:
            thumbnails[index] = t['url']
            index += 1

        return song['formats'][0]['url'], thumbnails

    @staticmethod
    async def extract_song(url: str, loop: AbstractEventLoop = None, executor: Executor = ThreadPoolExecutor()) -> \
            tuple[str, str]:
        """
        Execute SongExtractor.extract_song() with asyncio executor

        Returns
        -------
        Tuple
            Extracted song info
        """
        if not loop:
            loop = get_running_loop()
        result = await loop.run_in_executor(executor, functools.partial(SongExtractor.extract_song_blocking, url))
        return result
