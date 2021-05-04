import os
import pathlib

_root_dir: os.PathLike = pathlib.Path(__file__).parent.parent.parent


def set_root_path(path: os.PathLike):
    global _root_dir
    _root_dir = path


def get_root_path() -> os.PathLike:
    global _root_dir
    return _root_dir


def get_default_prefix():
    return ','


def get_default_language():
    return 'en'
