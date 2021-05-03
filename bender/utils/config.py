# import json
# from os import path
#
# DEFAULT_SETTING = {
#
#
#
# }
import configparser
import os

DEFAULT_CONFIG = {
    'YT_MUSIC': {
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
        self.update(**DEFAULT_CONFIG)
        for key in settings.keys():
            if not (key in DEFAULT_CONFIG.keys()):
                raise AttributeError(f"Unexpected keyword argument {key}")

        self.update(**settings)
        super().__init__()

    @staticmethod
    def _check_types(_dict: dict):
        for key in DEFAULT_CONFIG.keys():
            try:
                if not isinstance(_dict[key], type(DEFAULT_CONFIG[key])):
                    raise TypeError(f"Option {key} has invalid value")
            except KeyError:
                raise AttributeError(f"Missing required option {key}")

    def load(self, path: os.PathLike):
        if not os.path.exists(path):
            raise ValueError("Path is doesn't exist")
        try:
            file = open(path, 'r')
        except Exception:
            raise
        try:
            config = configparser.ConfigParser()
            config.read_file(file)
        except Exception:
            raise
        file.close()
        loaded = Config.parse_values(Config.to_dict(config))
        Config._check_types(loaded)
        self.update(**loaded)

    @staticmethod
    def generate_new(path: os.path):
        config = Config.to_config(DEFAULT_CONFIG)

        with open(path, 'w') as configfile:  # save
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
            elif isinstance(dictionary[key], str):
                if dictionary[key] or len(dictionary[key]) == 0 or dictionary[key] == 'None':
                    parsed[key] = None
                    continue
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
                parsed[key] = dictionary[key]

        return parsed

    @staticmethod
    def to_dict(config: configparser.ConfigParser):
        parsed = {}
        for section in config.sections():
            parsed[section] = dict(**config[section])

        return parsed


