import gettext
import os
import pathlib
from warnings import warn

import bender.utils.temp as _temp

# https://phrase.com/blog/posts/translate-python-gnu-gettext/

__all__ = ['MessageHandler']



class MessageHandler(object):
    def __init__(self, dir: os.PathLike = pathlib.Path("locales")):
        self.locales = dict()

    def get_text(self, args: str, *, language='en'):
        return self.locales[language].gettext(args)

    def load_translations(self, path: os.PathLike):
        if not os.path.exists(path):
            raise ValueError("Path doesn't exist")
        for p in os.listdir(path):

            if os.path.isdir(os.path.join(path, p)):
                try:
                    self.locales[p] = gettext.translation('messages', localedir=path, languages=[p])
                except Exception as e:
                    warn(f"Couldn't load language file {os.path.join(path, p)} due to error: {e}")
    def setup(self):
        self.load_translations(pathlib.Path(os.path.join(_temp.get_root_path(), "resources\\locales")))
        for lang in self.locales:
            self.locales[lang].install()
        global get_text
        get_text = self.locales['en'].gettext

    def get_loaded(self) -> tuple:
        return tuple(self.locales.keys())
