import gettext

# https://phrase.com/blog/posts/translate-python-gnu-gettext/


# el = gettext.translation('base', localedir='locales', languages=['el'])
# el.install()
get_text = gettext.gettext


class MessageHandler(object):
    def __init__(self, dir: str = "locales"):
        gettext.find('base', 'locales')