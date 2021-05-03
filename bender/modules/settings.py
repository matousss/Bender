import asyncio
import os
import pathlib
import sqlite3
import typing

from discord import Message, Embed
from discord.ext.commands import Cog, group, Context

import bender.utils.temp as _temp
from bender.bot import BenderCog, Bender as Bot


def setup(bot: Bot):
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
# todo messages shits
class Settings(BenderCog, description="cog_settings_description"):
    def __init__(self, bot):

        self._database = Database(os.path.join(_temp.get_root_path(), "resources\\guild_settings.sqlite"))

        self.get_prefix = self._database.executor_get_prefix
        super().__init__(bot)

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
        if not ctx.subcommand_passed:
            embed = Embed(color=0xff0000)
            embed.title = self.get_text("possible_settings")
            embed.description = ""
            for subcommand in ctx.bot.get_command("setting").commands:
                embed.description += f"``{subcommand.name}`` - " \
                                     f"{subcommand.description if subcommand.description else 'NaN'}\n"
            await ctx.send(embed=embed)

    @setting.command(name="prefix", description="command_setting_prefix_description",
                     usage="command_setting_prefix_usage")
    async def prefix(self, ctx: Context, *, args: typing.Optional[str] = None):
        if not args:
            await ctx.send(self.get_text("%s current_prefix") % ctx.bot.get_prefix(ctx.message))
        else:
            args = args.lstrip()
            if len(args) > 5:
                await ctx.send(self.get_text("prefix_too_long_error"))
            else:
                loop = asyncio.get_running_loop()
                task = loop.run_in_executor(None, self._database.set_prefix, ctx.guild.id, args)
                try:
                    await asyncio.wait_for(task, timeout=10)
                except asyncio.TimeoutError:
                    await ctx.send(self.get_text("unknown_error_setting_prefix"))
                await ctx.send(self.get_text("%s current_prefix") % f"{args}")

    @setting.command(name="language", aliases=["lang"], description="command_setting_language_description",
                     usage="command_setting_language_usage")
    async def language(self, ctx: Context, *, args: typing.Optional[str] = None):

        try:
            if not args:
                loop = asyncio.get_running_loop()
                task = loop.run_in_executor(None, self._database.get_language, ctx.guild.id)
                current_language = await asyncio.wait_for(task, timeout=10)
                await ctx.send(self.get_text("%s current_language") % f"``{current_language}``")
            elif args == 'languages':
                sb = ""
                if ctx.bot.loaded_languages:
                    for lang in ctx.bot.loaded_languages:
                        sb += f"``{lang}``, "
                        await ctx.send(self.get_text("%s possible_languages") % sb[:-2])
                else:
                    await ctx.send("error_no_languages")
            elif ctx.bot.loaded_languages and args in ctx.bot.loaded_languages:
                args = args.lstrip()
                loop = asyncio.get_running_loop()
                task = loop.run_in_executor(None, self._database.set_language, ctx.guild.id, args)

                await asyncio.wait_for(task, timeout=10)

                await ctx.send(self.get_text("%s current_language") % f"``{args}``")
            else:
                await ctx.send(self.get_text("setting_not_supported_language_error"))

        except asyncio.TimeoutError:
            await ctx.send(self.get_text("unknown_error_setting"))


class Database(object):
    def __init__(self, db_path: typing.Union[os.PathLike, str]):
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
        with self.connect() as connection:
            connection.execute("""
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
        # todo default prefix load from config
        return ","

    def set_prefix(self, guild_id: int, prefix: str):
        with self.connect() as connection:
            connection.execute("""
            UPDATE guilds
                SET prefix = ?
            WHERE id == ?
            """, (prefix, guild_id))

    def get_language(self, guild_id: int):
        with self.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(f"""
                SELECT language FROM guilds WHERE id == ?
            """, (guild_id,))
        return cursor.fetchone()[0]

    def set_language(self, guild_id: int, prefix: str):
        with self.connect() as connection:
            connection.execute("""
            UPDATE guilds
                SET language = ?
            WHERE id == ?
            """, (prefix, guild_id))

    def exist_guild(self, guild_id: int):
        with self.connect() as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM guilds WHERE id == ?", (guild_id,))
            guild = cursor.fetchone()
        if guild:
            return True
        return False

    def clean_unused(self, guild_ids: typing.Iterable, loaded_languages):
        with self.connect() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM guilds")
            guilds = cursor.fetchall()
        to_delete = []
        to_repair_lang = []
        for guild in guilds:
            if not guild[0] in guild_ids:
                to_delete.append(guild[0])
            elif not guild[2] in loaded_languages:
                to_repair_lang.append(guild[0])

        if to_delete:
            with connection:
                for d in to_delete:
                    connection.execute("""
                    DELETE FROM guilds WHERE id == ?
                    """, (d,))
        if to_repair_lang:
            with self.connect() as connection:
                for guild_id in to_repair_lang:
                    connection.execute("""
                                    UPDATE guilds
                                        SET language = ?
                                    WHERE id == ?
                                    """, ('en', guild_id,))
                # todo load default lang

    async def executor_get_prefix(self, bot=None, message: Message = None):
        if not message.guild:
            return ","
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
        self.clean_unused(guild_ids, bot.loaded_languages)
