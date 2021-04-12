from youtube_dl import YoutubeDL
import youtube_dl
from discord.player import FFmpegPCMAudio

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

#yt = YoutubeDL()
j= yt.extract_info("ytsearch1: moonage daydream", download = False)
if 'entries' in j:
    j = j['entries'][0]


print(j)

FFmpegPCMAudio()