# utils.py
import time

import discord
from discord.ext import commands
from dotenv import load_dotenv
import os.path
from discord.ext.commands import CommandNotFound

import bender
from bender.modules import *


load_dotenv()
TOKEN = os.environ.get("DISCORD_TOKEN")
PREFIX = str(os.environ.get("PREFIX"))
VERSION = bender.__version__




intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=str(PREFIX), intents=intents)



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
        #await ctx.send("Ty chceš moc věcí najednou! Počkej `" + str(int(error.cooldown.per)) + "s` saláme!")
        await ctx.send("Messages.on_cooldown"+" `" + str(int(error.cooldown.per)) + "s`!")
        return
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.send("Messages.missings_param")
        return
    raise error


def init_modules():
    bot.add_cog(audio.YoutubeMusic(bot))
    #bot.add_cog(bender.modules.audio.SoundBoard(bot))
    #bot.add_cog(modules.utils.Greetings(bot))
    bot.add_cog(utils.Utils(bot))
    bot.add_cog(utils.Moderation(bot))
    bot.add_cog(shits.Shits(bot))

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


bot.run(TOKEN)
