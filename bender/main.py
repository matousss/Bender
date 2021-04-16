# utils.py
import logging
import os.path
import sys
import time

import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound
from dotenv import load_dotenv

import bender
from bender.modules.audio.cogs import VoiceClientCommands, YoutubeMusic
from bender.global_settings import DEBUG
#logging.basicConfig(filename="fuck.log", level=logging.DEBUG )
load_dotenv()
TOKEN = os.environ.get("DISCORD_TOKEN")
PREFIX = str(os.environ.get("PREFIX"))
VERSION = bender.__version__
prefixes = {
    'default': ',',
    '767788412446048347': 'ß'
}


# todo option to select any prefix per server

async def prefix(bot, message: discord.Message):
    try:
        prefix = prefixes[str(message.guild.id)]
    except KeyError:
        prefix = prefixes['default']

    print(str(message.guild.id) + " " + prefix)
    return prefix

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=prefix, intents=intents, owner_id=494216665664323585)


@bot.event
async def on_command(command):
    print("<INFO> " + str(command.author.name) + "#" + str(command.author.id) + " executed command " + str(
        command.command))


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    if isinstance(error, discord.ext.commands.errors.NotOwner):
        await ctx.send("Messages.error_not_owner " + (ctx.author.mention) + "!")
    if isinstance(error, discord.ext.commands.errors.CommandOnCooldown):
        # await ctx.send("Ty chceš moc věcí najednou! Počkej `" + str(int(error.cooldown.per)) + "s` saláme!")
        await ctx.send("Messages.on_cooldown" + " ``" + str(int(error.cooldown.per)) + "s``!")
        return
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.send("Messages.missing_parameters")
        return
    raise error


def init_modules():
    # bot.add_cog(audio.YoutubeMusic(bot))
    # #bot.add_cog(bender.modules.audio.SoundBoard(bot))
    # #bot.add_cog(modules.utils.Greetings(bot))
    # bot.add_cog(utils.Utils(bot))
    # bot.add_cog(utils.Moderation(bot))
    # bot.add_cog(shits.Shits(bot))
    bot.add_cog(VoiceClientCommands(bot))
    bot.add_cog(YoutubeMusic(bot))
    pass


@bot.event
async def on_ready():


    print("\n\n" + f'{bot.user} has connected to Discord!\n\n')

    print("Connected to servers:")
    for guild in bot.guilds:
        print(str(guild) + " (" + str(guild.id) + ")")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=PREFIX + "help"))
    print("\n\n\n\nBender " + VERSION + " started!")


@bot.event
async def on_guild_join(guild):
    if guild.system_channel:
        await guild.system_channel.send("I am Bender please insert girder")

#todo run options
if __name__ == '__main__':
    for arg in sys.argv:
        if arg == "-thomashadneverseensuchabullshitbefore":
            DEBUG = True
    print("Starting...\n\n")
    init_modules()
    bot.run(TOKEN)


