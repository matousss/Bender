import gettext
import os
import typing
from warnings import warn

# https://phrase.com/blog/posts/translate-python-gnu-gettext/

__all__ = ['MessageHandler']


class MessageHandler(object):
    def __init__(self):
        self.locales = dict()

    def get_text(self, message: str, language: str = 'en'):

        return self.locales[language].gettext(message)

    def load_translations(self, path: os.PathLike):
        if not os.path.exists(path):
            raise ValueError("Path doesn't exist")
        for p in os.listdir(path):

            if os.path.isdir(os.path.join(path, p)):
                try:
                    self.locales[p] = gettext.translation('messages', localedir=path, languages=[p])
                except Exception as e:
                    warn(f"Couldn't load language file {os.path.join(path, p)} due to error: {e}")

    def setup(self, path: typing.Union[os.PathLike, str]):
        self.load_translations(path)
        for lang in self.locales:
            self.locales[lang].install()

    def get_loaded(self) -> tuple:
        return tuple(self.locales.keys())
