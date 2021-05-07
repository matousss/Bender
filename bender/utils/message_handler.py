import gettext
import os
import sys
import typing

from bender.utils.temp import get_default_language

# https://phrase.com/blog/posts/translate-python-gnu-gettext/

__all__ = ['MessageHandler']


class NoSuchLanguageError(Exception):
    """Raised when trying to get message in not loaded language"""

    def __init__(self, language: str):
        self.language = language
        super().__init__(f"Language {language} isn't loaded")

    pass


class MessageHandler(object):
    """
    Object, which loads and holds all texts of all messages
    """

    def __init__(self):
        self._locales = dict()

    def get_text(self, message: str, language: str = get_default_language):
        """
        Get certain message in certain language and return it.

        Parameters
        ----------
        message
            Key of requested message

        language : str, optional
            Destination language, takes default, when not specified
            Must be in ``_locales`` otherwise method raise exception

        Returns
        -------
        str
            Text of message in given language

        Raises
        ------
        NoSuchLanguageError
            Raised when given language code is not in ``_locales``
        """
        try:
            return self._locales[language].gettext(message)
        except KeyError:
            raise NoSuchLanguageError(language)

    def load_translations(self, path: os.PathLike):
        if not os.path.exists(path):
            raise ValueError("Path doesn't exist")
        for p in os.listdir(path):

            if os.path.isdir(os.path.join(path, p)):
                try:
                    self._locales[p] = gettext.translation('messages', localedir=path, languages=[p])
                except Exception as e:
                    print(f"Couldn't load language file {os.path.join(path, p)} due to error: {e}", file=sys.stderr)

    def setup(self, path: typing.Union[os.PathLike, str]) -> None:
        """
        Look for `messages.mo` files in given path and load them

        Parameters
        ----------
        path : str, os.PathLike
            Path to directory with messages files
        """
        self.load_translations(path)
        for lang in self._locales:
            self._locales[lang].install()

    def get_loaded(self) -> tuple:
        """
        Get tuple of loaded languages keys

        Returns
        -------
        tuple
            All keys of loaded languages
        """
        return tuple(self._locales.keys())
