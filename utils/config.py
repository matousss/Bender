# import json
# from os import path
#
# DEFAULT_SETTING = {
#
#
#
# }

DEFAULT_CONFIG = {
    'debug': False,
    'encrypt_token': True,
    'token': 'ODAxMDc1NDc5Mjg5MjY2MTk3.YAbZrQ.SfcU11qCo7SmHko-g0zkuChGKwk'
}

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


pass


