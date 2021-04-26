import subprocess

from discord.ext.commands import Context, CommandError

__all__ = ['Checks', 'CommandErrors']


class Checks:
    @staticmethod
    async def can_join_speak(ctx: Context):
        return ctx.me.guild_permissions.speak and ctx.me.guild_permissions.connect

    @staticmethod
    def checkFFMPEG() -> bool:
        """
        Check for ffmpeg/avconv
        """
        try:
            subprocess.check_call(['ffmpeg', '-version'],
                                  stdout=subprocess.DEVNULL,
                                  stderr=subprocess.STDOUT)
        except Exception:
            try:
                subprocess.check_call(['avconv', '-version'],
                                      stdout=subprocess.DEVNULL,
                                      stderr=subprocess.STDOUT)
            except Exception:
                return False
        return True


class CommandErrors:
    class NoChannel(CommandError):
        def __init__(self, *args):
            super().__init__(*args)

    pass