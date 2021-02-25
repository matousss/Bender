import json
import os
import sys

from discord.ext import commands

VERSION = os.environ.get("VERSION")
PREFIX = str(os.environ.get("PREFIX"))


class MessagesTexts:
    if not os.path.exists("lang.json"):
        os.system("generatelang.py 1")
    with open("lang.json", "r") as lang_file:
        lang = json.load(lang_file)
    try:
        message = lang["cs"]
        join = message[0]["join_message"]
        join_error = message[0]["join_error_message"]
        join_error_b = message[0]["join_error_message_b"]
        leave = message[0]["leave_message"]
        leave_error = message[0]["leave_error_message"]
        play = message[0]["play_message"]
        pause = message[0]["pause_message"]
        resume = message[0]["resume_message"]
        lang = message[0]["lang_message"]
        lang_error = message[0]["lang_error_message"]
        lang_error_b = message[0]["lang_error_b_message"]
        join_des = message[0]["join_command_des"]
        join_brief = message[0]["join_command_brief"]
        moveall = message[0]["moveall_message"]
        moveall_error = message[0]["moveall_error_message"] + " `" + PREFIX + "moveall <" + message[0][
            "name_world"] + ">`"
        moveall_error_b = message[0]["moveall_error_message_b"]
        info = message[0]["info_message"] + " " + str(VERSION)
        ping = message[0]["ping_message"]
    except KeyError as e:
        sys.exit("<ERROR> Cannot load message of key:" + str(e.args).replace("(", "").replace(",)", ""))

    def __init__(self):
        with open("lang.json", "r") as lang_file:
            lang = json.load(lang_file)
        message = lang["cs"]
        self.join = message[0]["join_message"]
        self.join_error = message[0]["join_error_message"]
        self.join_error_b = message[0]["join_error_message_b"]
        self.leave = message[0]["leave_message"]
        self.leave_error = message[0]["leave_error_message"]
        self.play = message[0]["play_message"]
        self.pause = message[0]["pause_message"]
        self.resume = message[0]["resume_message"]
        self.lang = message[0]["lang_message"]
        self.lang_error = message[0]["lang_error_message"]
        self.lang_error_b = message[0]["lang_error_b_message"]
        self.join_des = message[0]["join_command_des"]
        self.join_brief = message[0]["join_command_brief"]
        self.moveall = message[0]["moveall_message"]
        self.moveall_error = message[0]["moveall_error_message"] + " `" + PREFIX + "moveall <" + message[0][
            "name_world"] + ">`"
        self.moveall_error_b = message[0]["moveall_error_message_b"]
        self.info = message[0]["info_message"] + " v" + VERSION
        self.ping = message[0]["ping_message"]


class MessagesHandler:
    def __init__(self, bot):
        self.bot = bot
        print("Initialized modules.messages.Messages")

    async def sendMessage(self, ctx: commands.Context, content: str):
        await ctx.send(content)
        pass

    pass
