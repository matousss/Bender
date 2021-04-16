YTDL_OPTIONS = {
    'format': 'worstaudio/worst',
    'extractaudio': True,
    'audioformat': 'mp3',
    # 'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    # 'restrictfilenames': True,
    'noplaylist': False,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'no_warnings': False,
    # 'default_search': 'auto',
    'source_address': '0.0.0.0',
    'writesubtitles': False,
    # 'geo_bypass': True,
    'quiet': True,
    'extract_flat': True,
    'sleep_interval': 15,
    'call_home': False,
    'prefer_ffmpeg': True
}

YTDL_OPTIONS_INFO_ONLY = YTDL_OPTIONS
YTDL_OPTIONS_INFO_ONLY['extract_flat'] = True

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                  'options': '-vn'}
