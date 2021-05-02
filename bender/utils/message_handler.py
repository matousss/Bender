import gettext

# https://phrase.com/blog/posts/translate-python-gnu-gettext/


# el = gettext.translation('base', localedir='locales', languages=['el'])
# el.install()
import os

locales = dict()


def get_text(args: str):
    if args.startswith('%'):
        print(f"<DEBUG> Asked for: {args}")

    return gettext.gettext(args)


def load_translations(path: os.PathLike):
    if not os.path.exists(path):
        raise ValueError("Path doesn't exist")
    for p in os.listdir(path):

        if os.path.isdir(os.path.join(path, p)):
            locales[p] = gettext.translation('messages', localedir=path, languages=[p])


class MessageHandler(object):
    def __init__(self, dir: str = "locales"):
        gettext.find('base', 'locales')


load_translations("D:\\_Files\\PycharmProjects\\bender\\locales")

for l in locales:
    locales[l].install()
get_text = locales['en'].gettext
