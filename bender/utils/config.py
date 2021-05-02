# import json
# from os import path
#
# DEFAULT_SETTING = {
#
#
#
# }
import configparser
import json
import os
from typing import Iterable, Union

DEFAULT_CONFIG = {
    'token': 'ODAxMDc1NDc5Mjg5MjY2MTk3.YAbZrQ.SfcU11qCo7SmHko-g0zkuChGKwk'}

DEFAULT_CONFIG_1 = {
    'BASE': {
        'token': '',
    },
    'YT_MUSIC': {
        'ffmpeg_avconv_path': None,
        'max_queue_size': 20,
        'max_song_length': 7200,
        'best_quality': False,
        'max_idle_time': 180,
        'max_paused_time': 360
    }
}
__all__ = ['Config']


class Config(dict):
    #
    #
    # if path.exists("settings.json"):
    #
    #
    # else:
    #     with open("settings.json", "w") as file:
    #         json.dump()

    def __init__(self, **settings):
        self.update(DEFAULT_CONFIG)
        super().__init__()

    def load(self, path: os.path):
        if os.path.exists(path):
            raise ValueError()
        try:
            file = open(path, 'r')
        except Exception:
            raise
        try:
            config = configparser.ConfigParser()
            config.read_file(file)
        except Exception:
            raise
        self.update(Config.parse_values(Config.to_dict(config)))
        file.close()

    def load_all(self, paths: Iterable[Union[str, os.PathLike]]):
        for path in paths:
            self.load(path)

    @staticmethod
    def generate_new(path: os.path, *, modules: list = None, default: dict = None):
        config = Config.to_config(DEFAULT_CONFIG_1)

        with open('config.ini', 'w') as configfile:  # save
            config.write(configfile)

    @staticmethod
    def to_config(config: dict):
        parsed = configparser.ConfigParser()

        for section in config.keys():
            parsed_section = str(section).upper()
            parsed.add_section(parsed_section)
            for option in config[section].keys():
                parsed.set(section, option, str(config[section][option]))
        return parsed

    @staticmethod
    def parse_values(dictionary: dict):
        parsed = {}
        for key in dictionary.keys():
            if isinstance(dictionary[key], dict):
                parsed[key] = Config.parse_values(dictionary[key])

            if isinstance(dictionary[key], str):
                if dictionary[key] or len(dictionary[key]) == 0 or dictionary[key] == 'None':
                    parsed[key] = None
                try:
                    parsed[key] = int(dictionary[key])
                    continue
                except Exception:
                    pass

                if dictionary[key] == 'True':
                    parsed[key] = True
                    continue
                if dictionary[key] == 'False':
                    parsed[key] = False
                    continue

        return parsed

    @staticmethod
    def to_dict(config: configparser.ConfigParser):
        parsed = {}
        for section in config.sections():
            parsed[section] = dict(**config[section])

        return parsed


# path = os.path.abspath(os.path.join(".\\config.ini"))
# print(path)
# Config.generate_new(path)
#
# c = Config()
# c.load(path)
# print(c)
