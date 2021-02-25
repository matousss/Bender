#generatelang.py
import json

DEFAULT_LANG = {}
DEFAULT_LANG["en"] = []
DEFAULT_LANG["en"].append({
    "join_message" : "Joined the ",
    "join_error_message" : "Error while joining the",
    "join_error_message_b": "Error while joining the channel",
    "leave_message" : "Leaved the channel",
    "leave_error_message" :"I'm already in your channel",
    "play_message" : "Playing ",
    "pause_message" : ":pause_button:",
    "resume_message" : ":arrow_forward:",
    "lang_message": "Set language: `English`",
    "lang_error_message" : "Error, language didn't change!\nValid language codes:",
    "lang_error_b_message" : "I'm already speaking this language!",
    "join_command_des" : "Connect bot to same voice channel as you",
    "join_command_brief" : "Connect bot to same voice channel as you",
    "moveall_message": "I successfully moved everyone to:",
    "moveall_error_message": "Wrong syntax! Please use:",
    "name_world": "name",
    "moveall_error_message_b": "Ther's no channel named:",
    "info_message" : "Hello, I'm Bender",
    "ping_message" : "Bot ping is:"
})
DEFAULT_LANG["cs"] = []
DEFAULT_LANG["cs"].append({
    "join_message" : "No jó, však už jdu do ",
    "join_error_message" : "Kam se mám asi připojit ty saláme?",
    "join_error_message_b": "Vžyť stojím vedle tebe buřte",
    "leave_message" : "Stejně tu nechci být",
    "leave_error_message" : "Nikde nejsem a nikam nejdu",
    "play_message" : "Vždť už přehrávám, tak zavři chlebárnu",
    "pause_message" : ":pause_button:",
    "resume_message" : ":arrow_forward:",
    "lang_message" : "Nastaven jazyk: `Čeština`",
    "lang_error_message" : "Chyba, jazyk nebyl nastaven! / Error, language didn't change!\nPlatné jazykové kódy / Valid language codes:",
    "lang_error_b_message" : "Tímhle jazykem už mluvím!",
    "join_command_des": "Připojí bota do tvého hlasového kanálu",
    "join_command_brief": "Připojí bota do tvého hlasového kanálu",
    "moveall_message" : "Přesunul jsem všechny do:",
    "moveall_error_message" : "Špatná syntaxe! Použij:",
    "name_world": "jméno",
    "moveall_error_message_b" : "Na tomto serveru není kanál:",
    "info_message" : "Ahoj, já jsem Bender",
    "ping_message" : "Odezva bota je:"
})
LANGCODES = ["en", "cs"]
with open("lang.json", "w") as lang:
    json.dump(DEFAULT_LANG, lang)
