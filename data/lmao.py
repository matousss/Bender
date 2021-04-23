import asyncio
import functools
from asyncio import wait_for
from concurrent.futures.thread import ThreadPoolExecutor

from youtube_dl import YoutubeDL

yt = YoutubeDL({
    'format': 'bestaudio',
    'extractaudio': True,
    'audioformat': 'mp3',
    # 'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    # 'restrictfilenames': True,
    'noplaylist': False,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': False,
    'no_warnings': False,
    'default_search': 'auto',
    # 'source_address': '0.0.0.0',
    'geo_bypass': True,
    'simulate': True,
    'keepvideo': False
})

yt = YoutubeDL()


# if 'entries' in j:
#     j = j['entries'][0]
#
#
# print(j)
async def hovno():
    loop = asyncio.get_running_loop()

    task = loop.run_in_executor(ThreadPoolExecutor(),
                                functools.partial(yt.extract_info, "ytsearch1: moonage daydream", download=False))
    return await wait_for(task, timeout=None)
    j = yt.extract_info("ytsearch1: moonage daydream", download=False)
    print(str(j))


async def start():
     await hovno()
     await hovno()
     await hovno()
     await hovno()
     await hovno()


if __name__ == '__main__':
    loop = asyncio.AbstractEventLoop()
    loop.run_forever()
    task = asyncio.create_task(start)
    asyncio.run_coroutine_threadsafe(task, loop)




