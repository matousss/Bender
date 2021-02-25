# bender.py
import asyncio
import functools
import os
import re
import sys
import time
import typing

import discord
import youtube_dl
from discord.ext import commands
from dotenv import load_dotenv
import json
import asyncio
from async_timeout import timeout
import os.path
from os import path
from discord.ext.commands import CommandNotFound
from threading import Thread
from googletrans import Translator
import pafy
from modules.messages import MessagesTexts as Messages
import modules.music
import modules.shits
import modules.utils

load_dotenv()
TOKEN = os.environ.get("DISCORD_TOKEN")
PREFIX = str(os.environ.get("PREFIX"))
VERSION = os.environ.get("VERSION")
LANGCODES = ["en", "cs"]


class Settings:
    language = "cs"


intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=str(PREFIX), intents=intents)


@bot.command(name="language", aliases=["lang"])
async def _language(ctx, *, code: str = None):
    if code == Settings.language:
        await ctx.send(Messages.lang_error_b)
        return
    if code is not None:
        for s in LANGCODES:
            if s == code:
                Settings.language = code
                Messages.__init__()
                await ctx.send(Messages.lang)
                return
    codes = ""
    for s in LANGCODES:
        codes = codes + "\n" + "`" + s + "`"

    else:
        await ctx.send(Messages.lang_error + codes)
    pass


@bot.event
async def on_command(command):
    print("<INFO> " + str(command.author.name) + "#" + str(command.author.id) + " executed command " + str(
        command.command))


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    if isinstance(error, discord.ext.commands.errors.NotOwner):
        await ctx.send("Vyser si oko " + (ctx.author.mention) + "!")
    if isinstance(error, discord.ext.commands.errors.CommandOnCooldown):
        await ctx.send("Ty chceš moc věcí najednou! Počkej `" + str(int(error.cooldown.per)) + "s` saláme!")
        return
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.send("Chybí ti parametry!")
        return
    raise error


def init_modules():
    bot.add_cog(modules.music.YoutubeMusic(bot))
    bot.add_cog(modules.music.SoundBoard(bot))
    bot.add_cog(modules.utils.Greetings(bot))
    bot.add_cog(modules.utils.Utils(bot))
    bot.add_cog(modules.utils.Moderation(bot))
    bot.add_cog(modules.shits.Shits(bot))

    pass


@bot.event
async def on_ready():
    print("Starting...\n\n")
    init_modules()
    print("\n\n" + f'{bot.user} has connected to Discord!\n\n')

    print("Connected to servers:")
    for guild in bot.guilds:
        print(str(guild) + " (" + str(guild.id) + ")")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=PREFIX + "help"))
    time.sleep(1)
    print("\n\n\n\nBender " + VERSION + " started!")


@bot.event
async def on_guild_join(guild):
    if guild.system_channel:
        await guild.system_channel.send("I am Bender please insert girder")


# @bot.event
# async def on_message(message):
#    if message.author == bot.user:
#        return
#    if message.content.startswith("f"):
#
#        await message.channel.send("f")

bot.run(TOKEN)
