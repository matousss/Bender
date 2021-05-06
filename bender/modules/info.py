from typing import Optional

from discord import Embed
from discord.ext.commands import Cog, command, Context, cooldown, Command, Group

import bender
import bender.utils.bender_utils
import bender.utils.message_handler
from bender.bot import BenderCog

__all__ = ['Info']


def setup(bot):
    bot.remove_command('help')
    bot.add_cog(Info(bot))


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


class Info(BenderCog, name="Information", description="cog_info_description"):
    def __init__(self, bot):
        super().__init__(bot)

    @command(name="info", description="command_info_description", usage="")
    async def info(self, ctx: Context):
        await ctx.send(self.get_text("%s info", await self.get_language(ctx)) % f'``{bender.__version__}``')
        pass

    @command(name="ping", description="command_ping_description",
             usage="")
    async def ping(self, ctx: Context):
        await ctx.send(self.get_text('%s ping', await self.get_language(ctx)) %
                       f"``{str(round(float(ctx.bot.latency) * 1000.0))} ms``")

    @staticmethod
    def have_uncategorized_commands(bot):
        for _command in bot.walk_commands():
            if not _command.cog:
                return True
        return False

    @command(name="help", description="command_help_description",
             usage="command_help_usage")
    @cooldown(1, .5)
    async def help(self, ctx: Context, *, args: Optional[str] = None):
        lang = await ctx.bot.get_language(ctx)
        embed = Embed(color=0xff0000)
        args = args.lower() if args else None

        if not args:
            # show default help
            for cog in ctx.bot.cogs:
                cog: Cog = ctx.bot.get_cog(cog)
                embed.title = self.get_text("help_categories", lang)
                embed.description = self.get_text("help_categories_description", lang)
                embed.add_field(name=cog.qualified_name,
                                value=self.get_text(cog.description, lang) if
                                cog.description else 'NaN')
            if Info.have_uncategorized_commands(ctx.bot):
                embed.add_field(name='Other', value=self.get_text("commands_with_no_category",
                                                                  lang))

                embed.set_footer(text=self.get_text("command_help_tips", lang))

        elif args.lower() == "commands":
            # show all possible commands
            embed.title = self.get_text("possible_commands", lang)
            embed.set_footer(text=self.get_text("possible_command_tips", lang))
            for cog in ctx.bot.cogs:
                commands = ""
                cog = ctx.bot.get_cog(cog)
                for _command in cog.walk_commands():
                    commands += f"``{_command.qualified_name}``, "
                if len(commands) > 0:
                    embed.add_field(name=cog.qualified_name, value=commands[:-2])
            commands = ""
            for _command in ctx.bot.walk_commands():
                if not _command.cog:
                    commands += f"``{_command.qualified_name}``, "
            if len(commands) > 0:
                embed.add_field(name=self.get_text("no_category", lang), value=commands[:-2])

        elif args.lower() == 'other':
            # show commands without category
            if not Info.have_uncategorized_commands(ctx.bot):
                await ctx.send(self.get_text("no_category_or_command", lang))
                return
            embed.title = self.get_text('%s showing_help_for',
                                        lang) % self.get_text("commands_with_no_category",
                                                              lang)
            commands = ""
            for _command in ctx.bot.walk_commands():
                if not _command.cog:
                    commands += f"``{_command.qualified_name}``, "
            embed.add_field(name=self.get_text("possible_commands", lang), value=commands[:-2])

        else:
            # search for command/category
            args = args.lower()
            for _cog in ctx.bot.cogs:
                _cog: str
                if args == _cog.lower():
                    _cog: Cog = ctx.bot.get_cog(_cog)
                    embed.title = self.get_text("%s showing_help_for",
                                                lang) % _cog.qualified_name
                    embed.description = self.get_text(_cog.description, lang) \
                        if _cog.description else ""
                    commands = ''
                    for _command in _cog.walk_commands():
                        commands += f"``{_command.qualified_name}``, "
                    commands = commands[:-2]
                    if commands:
                        embed.add_field(name=self.get_text("possible_commands", lang),
                                        value=commands)

                    break

            else:
                _command: Command
                for _command in ctx.bot.walk_commands():
                    if args == _command.qualified_name.lower():
                        break
                    elif not _command.parent and args in _command.aliases:
                        break

                else:
                    await ctx.send(self.get_text("no_category_or_command", lang))
                    return

                embed.title = self.get_text("%s showing_help_for", lang) % _command.name
                embed.description = self.get_text(_command.description, lang) \
                    if _command.description else "NaN"
                if _command.usage is not None:
                    embed.add_field(name=self.get_text("command_usage", lang),
                                    value=f"{await ctx.bot.command_prefix(message=ctx.message)}"
                                          f"{_command.qualified_name} "
                                          f"""{(self.get_text(_command.usage, lang) if
                                                len(_command.usage) > 0 else '')
                                          if _command.usage is not None else 'NaN'}""",
                                    inline=False)
                if _command.aliases and len(_command.aliases) > 0:
                    embed.add_field(name=self.get_text("aliases", lang),
                                    value=''.join([f"``{alias}`` " for alias in _command.aliases]))

                if isinstance(_command, Group):
                    subcommands = ""
                    for sc in _command.commands:
                        subcommands += f"``{sc.name}``\n"
                    embed.add_field(name=self.get_text("subcommands", lang), value=subcommands)

        await ctx.send(embed=embed)

    pass
