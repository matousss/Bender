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

DEFAULT_CONFIG = {
    'token': 'ODAxMDc1NDc5Mjg5MjY2MTk3.YAbZrQ.SfcU11qCo7SmHko-g0zkuChGKwk',
    'YT_Music': {
        'max_queue_size': 20,
        'max_song_length': 7200,
        'best_quality': False
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
        if len(settings) == 0:
            settings = DEFAULT_CONFIG

        self.update(settings)
        super().__init__()

    def load(self, path: os.path):
        try:
            file = open(path, 'r')
        except Exception:
            raise
        try:
            data = json.load(file)
        except Exception:
            raise
        self = data

    @staticmethod
    def generate_new(path: os.path):
        config = configparser.ConfigParser()
        config['INTERPRETER']['path'] = 'python'  # update
        config['INTERPRETER']['default_message'] = 'Hey! help me!!'  # create

        with open('config.ini', 'w') as configfile:  # save
            config.write(configfile)


pass
# path = os.path.abspath(os.path.join(".\\config.json"))
# print(path)
# Config.generate_new(path)

