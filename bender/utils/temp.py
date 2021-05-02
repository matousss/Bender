import os
import pathlib

global_variables = {}


def test():
    print(global_variables)


_root_dir: os.PathLike = pathlib.Path(__file__)


def set_root_path(path: os.PathLike):
    global _root_dir
    _root_dir = path


def get_root_path():
    global _root_dir
    return _root_dir
