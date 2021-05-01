import discord.ext.commands

import bender.utils.bender_utils as bender_utils


@bender_utils.bender_module
class Settings(discord.ext.commands.Cog):
    def __init__(self, bot):
        self.bot: discord.ext.commands.Bot = bot
        self.bot.command_prefix = bender_utils.prefix

        print(f"Initialized {str(__name__)}")
