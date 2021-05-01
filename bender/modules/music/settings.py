# todo load from file
# warning do not change anything, if you don't understand how app works

YTDL_OPTIONS = {
        'format': 'worstaudio/worst',
        'extractaudio': True,
        'audioformat': 'mp3',
        'noplaylist': False,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'logtostderr': False,
        'no_warnings': False,
        'source_address': '0.0.0.0',
        'writesubtitles': False,
        'geo_bypass': True,
        'quiet': True,
        'extract_flat': True,
        'sleep_interval': 15,
        'call_home': False,
        'prefer_ffmpeg': True,

    }

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                  'options': '-vn'}
