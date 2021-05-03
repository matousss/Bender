import os
import pathlib

from bender.utils.config import Config

_root_dir: os.PathLike = pathlib.Path(__file__).parent.parent.parent

_configuration: Config = None

_loaded_languages = None

def set_root_path(path: os.PathLike):
    global _root_dir
    _root_dir = path


def get_root_path() -> os.PathLike:
    global _root_dir
    return _root_dir


def set_config(config: Config):
    global _configuration
    _configuration = config


def get_config() -> Config:
    global _configuration
    return _configuration
