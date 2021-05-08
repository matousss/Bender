import asyncio
import os
import pathlib
import sqlite3
import typing
from sqlite3.dbapi2 import Cursor

from discord import Message, Embed, Guild
from discord.ext.commands import group, Context, NoPrivateMessage, cooldown

import bender.utils.temp as _temp
from bender.bot import BenderCog


def setup(bot):
    cog = Settings(bot)

    bot.command_prefix = cog.get_prefix
    bot.database = cog.database
    bot.database.setup()
    bot.get_language = bot.database.executor_get_language
    cog.get_language = bot.get_language
    bot.add_cog(cog)


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
class Settings(BenderCog, description="cog_settings_description"):
    def __init__(self, bot):

        self._database = Database(os.path.join(_temp.get_root_path(), "resources\\guild_settings.sqlite"))

        self.get_prefix = self._database.executor_get_prefix
        super().__init__(bot)

    @BenderCog.listener()
    async def on_ready(self):
        loop = asyncio.get_running_loop()
        task = loop.run_in_executor(None, self._database.prepare_db, self.bot)
        await asyncio.wait_for(task, timeout=None)

    @BenderCog.listener()
    async def on_guild_join(self, guild: Guild):
        loop = asyncio.get_running_loop()
        task = loop.run_in_executor(None, self._database.add_guild, guild.id)
        await asyncio.wait_for(task, timeout=None)

    @BenderCog.listener()
    async def on_guild_remove(self, guild: Guild):
        loop = asyncio.get_running_loop()
        task = loop.run_in_executor(None, self._database.remove_guild, guild.id)
        await asyncio.wait_for(task, timeout=None)

    def cog_check(self, ctx: Context):
        if ctx.guild is None:
            raise NoPrivateMessage()
        return True

    @group(name="setting", aliases=["set"], description="command_setting_description",
           usage="command_setting_usage")
    @cooldown(1, 3)
    async def setting(self, ctx: Context):
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.send(self.get_text("user_missing_permissions_error", await self.get_language(ctx)))
            return
        if not ctx.subcommand_passed:
            lang = await self.get_language(ctx)
            embed = Embed(color=0xff0000)
            embed.title = self.get_text("possible_settings", lang)
            embed.description = ""
            for subcommand in ctx.bot.get_command("setting").commands:
                embed.description += f"``{subcommand.name}`` - " \
                                     f"""{self.get_text(subcommand.description, lang)
                                     if subcommand.description else 'NaN'}\n"""
            await ctx.send(embed=embed)

    @setting.command(name="prefix", description="command_setting_prefix_description",
                     usage="command_setting_prefix_usage")
    async def prefix(self, ctx: Context, *, args: typing.Optional[str] = None):
        if not args:
            await ctx.send(self.get_text("%s current_prefix",
                                         await self.get_language(ctx)) % f"``{await ctx.bot.get_prefix(ctx.message)}``")
        else:
            args = args.lstrip()
            if len(args) > 5:
                await ctx.send(self.get_text("prefix_too_long_error", await self.get_language(ctx)))
            else:
                loop = asyncio.get_running_loop()
                task = loop.run_in_executor(None, self._database.set_prefix, ctx.guild.id, args)
                try:
                    await asyncio.wait_for(task, timeout=10)
                except asyncio.TimeoutError:
                    await ctx.send(self.get_text("unknown_setting_prefix_error", await self.get_language(ctx)))
                    return
                await ctx.send(self.get_text("%s current_prefix", await self.get_language(ctx)) % f"``{args}``")

    @setting.command(name="language", aliases=["lang"], description="command_setting_language_description",
                     usage="command_setting_language_usage")
    async def language(self, ctx: Context, *, args: typing.Optional[str] = None):

        try:
            if not args:
                current_language = await self.get_language(ctx)

                await ctx.send(
                    self.get_text("%s current_language", current_language) % f"``{current_language}``")
            elif args == 'languages' or args == 'help':
                lang = await self.get_language(ctx)
                sb = ""
                if ctx.bot.loaded_languages:
                    for loaded in ctx.bot.loaded_languages:
                        sb += f"``{loaded}``, "
                    await ctx.send(self.get_text("%s possible_languages", lang) % sb[:-2])
                else:
                    await ctx.send(self.get_text("error_no_languages", lang))
            elif ctx.bot.loaded_languages and args in ctx.bot.loaded_languages:
                args = args.lstrip()
                loop = asyncio.get_running_loop()
                task = loop.run_in_executor(None, self._database.set_language, ctx.guild.id, args)

                await asyncio.wait_for(task, timeout=10)

                await ctx.send(self.get_text("%s current_language", await self.get_language(ctx)) % f"``{args}``")
            else:
                await ctx.send(self.get_text("setting_not_supported_language_error", await self.get_language(ctx)))

        except asyncio.TimeoutError:
            await ctx.send(self.get_text("unknown_setting_language_error", await self.get_language(ctx)))

    @property
    def database(self):
        return self._database


class Database(object):
    def __init__(self, db_path: typing.Union[os.PathLike, str]):
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
            CREATE TABLE IF NOT EXISTS guilds (
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

    def remove_guild(self, guild_id: int):
        with self.connect() as connection:
            connection.execute("""
            DELETE FROM guilds 
            WHERE EXISTS (SELECT id FROM guilds WHERE id == ?1)
            AND id == ?1             
            """, (guild_id,))

    def get_prefix(self, guild_id: int):

        connection = self.connect()
        try:
            with connection:
                cursor: Cursor = connection.cursor()
                cursor.execute(f"""
                    SELECT prefix FROM guilds WHERE id == ?
                """, (guild_id,))
                result = cursor.fetchone()
            if result:
                return result[0]
        finally:
            connection.close()
        # todo default prefix load from config
        return _temp.get_default_prefix()

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
            return _temp.get_default_prefix()
        loop = asyncio.get_running_loop()
        task = loop.run_in_executor(None, self.get_prefix, message.guild.id)
        try:
            prefix = await asyncio.wait_for(task, timeout=2)
            return prefix
        except TimeoutError:
            pass
        return _temp.get_default_prefix()

    async def executor_get_language(self, ctx: Context):

        if not ctx.guild:
            return _temp.get_default_language()
        loop = asyncio.get_running_loop()
        task = loop.run_in_executor(None, self.get_language, ctx.guild.id)
        try:
            lang = await asyncio.wait_for(task, timeout=2)
            return lang
        except TimeoutError:
            pass
        return _temp.get_default_language()

    def prepare_db(self, bot) -> None:
        guild_ids = []
        for guild in bot.guilds:
            self.add_guild(guild.id)
            guild_ids.append(guild.id)
        self.clean_unused(guild_ids, bot.loaded_languages)
