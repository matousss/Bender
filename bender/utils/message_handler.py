import gettext
import os
import pathlib

import bender.utils.temp

# https://phrase.com/blog/posts/translate-python-gnu-gettext/

locales = dict()


def get_text(args: str, *, language='en'):
    return locales[language].gettext(args)


def load_translations(path: os.PathLike):
    if not os.path.exists(path):
        raise ValueError("Path doesn't exist")
    for p in os.listdir(path):

        if os.path.isdir(os.path.join(path, p)):
            locales[p] = gettext.translation('messages', localedir=path, languages=[p])


class MessageHandler(object):
    def __init__(self, dir: os.PathLike = pathlib.Path("locales")):
        gettext.find('messages', dir)


def setup():
    load_translations(pathlib.Path(os.path.join(bender.utils.temp.get_root_path(), "resources\\locales")))
    global locales
    for l in locales:
        locales[l].install()
    global get_text
    get_text = locales['en'].gettext
