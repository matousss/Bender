import discord.ext.commands

import bender.utils
import bender.utils.bender_utils as bender_utils

get_text = bender.utils.message_handler.get_text


@bender_utils.bender_module
class Settings(discord.ext.commands.Cog, description=get_text("cog_settings_description")):
    def __init__(self, bot):
        self.bot: discord.ext.commands.Bot = bot
        self.bot.command_prefix = bender_utils.prefix

        print(f"Initialized {str(__name__)}")
