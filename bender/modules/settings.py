import discord.ext.commands
from discord.ext.commands import Bot

import bender.utils
import bender.utils.bender_utils as bender_utils

get_text = bender.utils.message_handler.get_text


def setup(bot: Bot):
    bot.add_cog(Settings(bot))


#
#
#
#
#
#
#
#
#
#


class Settings(discord.ext.commands.Cog, description="cog_settings_description"):
    def __init__(self, bot):
        self.bot: discord.ext.commands.Bot = bot
        self.bot.command_prefix = bender_utils.prefix

        print(f"Initialized {str(self.__class__.__name__)}")
