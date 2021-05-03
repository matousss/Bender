import asyncio
import os
import pathlib
import sqlite3
import typing

from discord import Message
from discord.ext.commands import Bot, Cog, group, Context, guild_only

import bender.utils.message_handler
import bender.utils.temp as _temp

get_text = bender.utils.message_handler.get_text


def setup(bot: Bot):
    print(command.qualified_name for command in bot.walk_commands())
    cog = Settings(bot)
    bot.add_cog(cog)

    bot.command_prefix = cog.get_prefix
    print(f"Initialized {cog.__class__.__name__}")


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

class Settings(Cog, description="cog_settings_description"):
    def __init__(self, bot):
        self.bot = bot

        self._database = Database(os.path.join(_temp.get_root_path(), "resources\\guild_settings.sqlite"))

        self.get_prefix = self._database.executor_get_prefix

    @Cog.listener()
    async def on_ready(self):
        loop = asyncio.get_running_loop()
        task = loop.run_in_executor(None, self._database.prepare_db, self.bot)
        await asyncio.wait_for(task, timeout=None)

    pass
    def cog_check(self, ctx):
        if ctx.guild:
            return True
        return False

    @group(name="setting", aliases=["set"], description="command_setting_description",
           usage="command_setting_usage")
    async def setting(self, ctx: Context):
        pass

    @setting.command(name="prefix", description="command_setting_prefix_description",
                    usage="command_setting_prefix_usage")
    async def prefix(self, ctx: Context, *, args: typing.Optional[str] = None):
        if not args:
            await ctx.send(get_text("%s current_prefix") % ctx.bot.get_prefix(ctx.message))
        else:
            args = args.lstrip()
            if len(args) > 5:
                await ctx.send(get_text("prefix_too_long_error"))
            else:
                loop = asyncio.get_running_loop()
                task = loop.run_in_executor(None, self._database.set_prefix, ctx.guild.id, args)
                try:
                    await asyncio.wait_for(task, timeout=10)
                except asyncio.TimeoutError:
                    await ctx.send(get_text("unknown_error_setting_prefix"))
                await ctx.send(get_text("%s current_prefix") % f"{args}")


class Database(object):
    def __init__(self, db_path: os.PathLike):
        # self.bot: Bot = bot
        # self.bot.command_prefix = bender_utils.prefix
        # print(f"Initialized {str(self.__class__.__name__)}")
        if not pathlib.Path(db_path).parent.exists():
            raise ValueError("Given path doesn't exist")
        self._db_path = db_path

    def connect(self):
        if pathlib.Path(self._db_path).parent.exists():
            return sqlite3.connect(self._db_path)
        else:
            raise ValueError("Given path doesn't exist")

    def setup(self):
        with self.connect():
            self._connection.execute("""
            CREATE TABLE if NOT EXISTS guilds (
                id INTEGER NOT NULL PRIMARY KEY,
                prefix CHARACTER(5) NOT NULL DEFAULT ',',
                language CHARACTER(3) NOT NULL DEFAULT 'en'
            );            
            """)

    def add_guild(self, guild_id: int):
        with self.connect() as connection:
            connection.execute(f"""
            INSERT INTO guilds (id) 
            SELECT (?1)
            WHERE NOT EXISTS (SELECT id FROM guilds WHERE id == ?1)""", (guild_id,))

    def get_prefix(self, guild_id: int):

        connection = self.connect()
        try:
            with connection:
                cursor = connection.cursor()
                cursor.execute(f"""
                    SELECT prefix FROM guilds WHERE id == ?
                """, (guild_id,))
                result = cursor.fetchone()
            if result:
                return result[0]
        finally:
            connection.close()
        # todo default prefix
        return ","

    def set_prefix(self, guild_id: int, prefix: str):
        with self.connect() as connection:
            connection.execute("""
            UPDATE guilds
                SET prefix = ?
            WHERE id == ?
            """, (prefix, guild_id))

    def get_language(self, guild_id: int):
        with self._connection:
            cursor = self._connection.cursor()
            cursor.execute(f"""
                SELECT language FROM guilds WHERE id == ?
            """, (guild_id,))
        return cursor.fetchone()[0]

    def exist_guild(self, guild_id: int):
        with self._connection:
            self._connection.row_factory = sqlite3.Row
            cursor = self._connection.cursor()
            cursor.execute("SELECT * FROM guilds WHERE id == ?", (guild_id,))
            guild = cursor.fetchone()
        if guild:
            return True
        return False

    def clean_unused(self, guild_ids: typing.Iterable):
        with self.connect() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id FROM guilds")
            guilds = cursor.fetchall()
        to_delete = []
        for guild in guilds:
            if not guild[0] in guild_ids:
                to_delete.append(guild[0])

        if to_delete:
            with connection:
                for d in to_delete:
                    connection.execute("""
                    DELETE FROM guilds WHERE id == ?
                    """, (d,))

    async def executor_get_prefix(self, bot=None, message: Message = None):

        loop = asyncio.get_running_loop()
        task = loop.run_in_executor(None, self.get_prefix, message.guild.id)
        try:
            prefix = await asyncio.wait_for(task, timeout=2)
            return prefix
        except TimeoutError:
            pass
        return ","

    def prepare_db(self, bot: Bot) -> None:
        guild_ids = []
        for guild in bot.guilds:
            self.add_guild(guild.id)
            guild_ids.append(guild.id)
        self.clean_unused(guild_ids)
