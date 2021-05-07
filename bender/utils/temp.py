import os

_root_dir: os.PathLike = None
"""Saved path to root folder"""


def set_root_path(path: os.PathLike):
    """Setter for :variable: `_root_dir` in order to make this information globally accessible"""
    global _root_dir
    _root_dir = path


def get_root_path() -> os.PathLike:
    """Returns path to root dir of app, if it's set before otherwise returns ``None``"""
    global _root_dir
    return _root_dir


# todo load from config file
def get_default_prefix():
    return ','


# todo load from config file, block not loaded languages
def get_default_language():
    return 'en'
