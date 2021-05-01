import gettext

# https://phrase.com/blog/posts/translate-python-gnu-gettext/


# el = gettext.translation('base', localedir='locales', languages=['el'])
# el.install()
get_text = gettext.gettext

def get_text(args: str):
    if args.startswith('%'):
        print(f"<DEBUG> Asked for: {args}")

    return gettext.gettext(args)

class MessageHandler(object):
    def __init__(self, dir: str = "locales"):
        gettext.find('base', 'locales')