import importlib
import logging
import os
import sys

import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound
from dotenv import load_dotenv

import bender
import bender.modules as modules
# print(sys.modules.keys())
from bender.utils.utils import BenderModuleError

load_dotenv()
TOKEN = os.environ.get("DISCORD_TOKEN")
PREFIX = str(os.environ.get("PREFIX"))
VERSION = bender.__version__
prefixes = {
    'default': ',',
    '767788412446048347': 'ß'
}


def import_from_dir(package_path, package_name):
    print(os.listdir(package_path))
    for file in os.listdir(package_path):
        print(f"file {file}")
        if not file.startswith('__'):
            if file.endswith(".py"):
                file = file.replace('.py', '')
                print(f"imported {package_name}.{file}")
                importlib.import_module(f'{package_name}.{file}')
                continue

            if not os.path.isdir(os.path.join(".", str(file))):
                print("hovno")
                # import_from_dir(package_path + file + "\\", f'{package_name}.{file}')
                try:
                    cogs = importlib.import_module(f'{package_name}.{file}').__cogs__
                except AttributeError:
                    logging.exception(BenderModuleError("BenderModule package have to have variable __cogs__\n"
                                                        f"which holds paths to cogs -> skipping {package_name}.{file}"))
                    continue

                for c in cogs:
                    c = c.replace('.\\', '').replace('.py', '')
                    print(c)
                    importlib.import_module(f'{package_name}.{file}.{c}')
                    print(f"imported {package_name}.{file}.{c}")
                pass

    pass


# todo option to select any prefix per server

async def prefix(bot, message: discord.Message):
    try:
        prefix = prefixes[str(message.guild.id)]
    except KeyError:
        prefix = prefixes['default']

    return prefix


intents = discord.Intents.default()
intents.members = True
BOT = commands.Bot(command_prefix=prefix, intents=intents, owner_id=494216665664323585)


@BOT.event
async def on_command(command):
    print("<INFO> " + str(command.author.name) + "#" + str(command.author.id) + " executed command " + str(
        command.command))


@BOT.event
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


@BOT.event
async def on_ready():
    print("\n\n" + f'{BOT.user} has connected to Discord!\n\n')

    print("Connected to servers:")
    for guild in BOT.guilds:
        print(str(guild) + " (" + str(guild.id) + ")")
    await BOT.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=PREFIX + "help"))
    print("\n\nBender " + VERSION + " started!")


@BOT.event
async def on_guild_join(guild):
    if guild.system_channel:
        await guild.system_channel.send("I am Bender please insert girder")


# todo run options
if __name__ == '__main__':
    for arg in sys.argv:
        if arg == "-thomashadneverseensuchabullshitbefore":
            DEBUG = True

    print("Starting...\n\n")
    import_from_dir(str(modules.__file__).replace('__init__.py', ''), 'modules')
    from modules import __cogs__
    for cog in __cogs__:
        BOT.add_cog(cog(BOT))
    BOT.run(TOKEN)
