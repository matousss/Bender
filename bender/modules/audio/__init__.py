__all__ = ['cogs', 'music', 'song']



try:
    from . import cogs

    try:
        __cogs__ = [cogs.VoiceClientCommands, cogs.YoutubeMusic]
    except NameError:
        import traceback
        from . import __name__

        traceback.print_exc()

except ImportError:
    import traceback
    from . import __name__
    from ...utils.utils import BenderModuleError
    raise BenderModuleError(f"Couldn't import module {str(__name__)}")

