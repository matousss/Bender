from typing import Optional

from discord import Embed
from discord.ext.commands import Cog, command, Context, Bot, cooldown, Command, Group

__all__ = ['Info']

import bender.utils.message_handler
import bender.utils.bender_utils
import bender

get_text = bender.utils.message_handler.get_text


@bender.utils.bender_utils.bender_module
class Info(Cog, name="Information", description=get_text("cog_info_description")):
    def __init__(self, bot: Bot):
        self.BOT: Bot = bot
        bot.remove_command('help')
        print(f"Initialized {str(__name__)}")

    @command(name="info", description=get_text("command_info_description"),
             help=get_text("command_info_help"), usage="")
    @cooldown(1, 10)
    async def _info(self, ctx):
        await ctx.send(get_text("%s info") % bender.__version__)
        pass

    @command(name="ping", description=get_text("command_ping_description"),
             help=get_text("command_ping_help"), usage="")
    @cooldown(1, 10)
    async def ping(self, ctx: Context):
        # print("<INFO> ping: "+str(float(bot.latency)*1000).split(".")[0] +"ms")
        await ctx.send(get_text('%s ping') % f"``{str(round(float(ctx.bot.latency) * 1000))}ms``")

    @command(name="help", description=get_text("command_help_description"),
             help=get_text("command_help_help"), usage=f"[{get_text('command')}/{get_text('category')}]")
    @cooldown(1, .5)
    async def help(self, ctx: Context, *, args: Optional[str] = None):
        embed = Embed(color=0xff0000)
        if not args:
            for cog in ctx.bot.cogs:
                cog: Cog = ctx.bot.get_cog(cog)
                embed.title = get_text("help_categories")
                embed.description = get_text("help_categories_description")
                embed.add_field(name=cog.qualified_name, value=cog.description if cog.description else 'NaN')
                embed.set_footer(text=get_text("command_help_tips"))
        elif args == "commands":
            embed.title = get_text("possible_commands")
            embed.set_footer(text=get_text("possible_command_tips"))
            for cog in ctx.bot.cogs:
                commands = ""
                cog = ctx.bot.get_cog(cog)
                for _command in cog.walk_commands():
                    # if _command.parent and isinstance(_command.parent, Group):
                    #     continue
                    commands += f"``{_command.qualified_name}``, "
                embed.add_field(name=cog.qualified_name, value=commands[:-2])
            commands = ""
            for _command in ctx.bot.walk_commands():
                if not _command.cog:
                    commands += f"``{_command.qualified_name}``, "
            if len(commands) > 0:
                embed.add_field(name=get_text("no_category"), value=commands[:-2])

        else:
            args = args.lower()
            for _cog in ctx.bot.cogs:
                _cog: str
                if args == _cog.lower():
                    _cog: Cog = ctx.bot.get_cog(_cog)
                    embed.title = get_text("%s showing_help_for") % _cog.qualified_name
                    embed.description = _cog.description
                    commands = ''
                    for _command in _cog.walk_commands():
                        commands += f"``{_command.qualified_name}``, "
                    commands = commands[:-2]

                    embed.add_field(name=get_text("possible_commands"), value=commands)

                    break

            else:
                _command: Command
                for _command in ctx.bot.walk_commands():
                    if args == _command.qualified_name.lower():
                        break
                    elif not _command.parent and args in _command.aliases:
                        break

                else:
                    await ctx.send(get_text("no_category_or_command"))
                    return

                embed.title = get_text("%s showing_help_for") % _command.name
                embed.description = _command.description if _command.description else "NaN"
                if _command.usage is not None:
                    embed.add_field(name=get_text("command_usage"), value=f"{ctx.bot.command_prefix()}"
                                                                          f"{_command.qualified_name} "
                                                                          f"{_command.usage}",
                                    inline=False)
                if _command.aliases and len(_command.aliases) > 0:
                    embed.add_field(name=get_text("aliases"), value=''.join([f"``{alias}`` "
                                                                             for alias in _command.aliases]))

                if isinstance(_command, Group):
                    subcommands = ""
                    for sc in _command.commands:
                        subcommands += f"``{sc.name}``\n"
                    embed.add_field(name=get_text("subcommands"), value=subcommands)

        await ctx.send(embed=embed)

    pass
