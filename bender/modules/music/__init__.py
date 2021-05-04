__all__ = ['youtube_music', 'music', 'song', 'settings']



try:
    import youtube_dl
except ImportError:
    from bender.utils.bender_utils import ExtensionLoadError
    raise ExtensionLoadError("youtube_dl is required to use music module")