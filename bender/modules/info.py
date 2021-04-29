from typing import Optional

from discord import Embed
from discord.ext.commands import Cog, command, Context, Bot, cooldown, Command, Group

__all__ = ['Info']

from bender.utils.message_handler import get_text
from bender.utils.utils import bender_module, prefix as _prefix
from bender import __version__

@bender_module
class Info(Cog, name="Information", description=get_text("cog_info_description")):
    def __init__(self, bot: Bot):
        self.BOT: Bot = bot
        bot.remove_command('help')
        print(f"Initialized {str(__name__)}")

    @command(name="info", description=get_text("command_info_description"),
             help=get_text("command_info_help"), usage="")
    @cooldown(1, 10)
    async def _info(self, ctx):
        await ctx.send(get_text("%s info") % __version__)
        pass

    @command(name="ping", description=get_text("command_ping_description"),
             help=get_text("command_ping_help"), usage="")
    @cooldown(1, 10)
    async def ping(self, ctx: Context):
        # print("<INFO> ping: "+str(float(bot.latency)*1000).split(".")[0] +"ms")
        await ctx.send(get_text('%s ping') % f"``{str(round(float(ctx.bot.latency) * 1000))}ms``")

    # @command(name="suicide")
    # @is_owner()
    # async def suicide(self, ctx):
    #     get_event_loop().stop()
    #     pass
    #
    # @command(name="deleteme", aliases=['dem'])
    # @guild_only()
    # async def deleteme(self, ctx, args):
    #     await ctx.message.delete()
    #     await ctx.send(get_text("%s smazal zprávu") % ctx.author.mention)

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
                embed.set_footer(text=get_text("command_help_description"))
        else:
            args = args.lower()
            for _cog in ctx.bot.cogs:
                if args == _cog.lower():
                    print(ctx.bot.get_cog(_cog))
                    break

            else:
                _command: Command
                for _command in ctx.bot.commands:
                    if args == _command.name.lower():
                        print(_command)
                        break
                else:
                    await ctx.send(get_text("no_category_or_command"))
                    return

                embed.title = get_text("%s showing_help_for") % _command.name
                embed.description = _command.description if _command.description else "NaN"
                if _command.usage:
                    embed.add_field(name=get_text("command_usage"), value=f"{_prefix(message=ctx.message)}"
                                                                          f"{_command.name} {_command.usage}",
                                    inline=False)
                if _command.aliases and len(_command.aliases) > 0:
                    embed.add_field(name=get_text("aliases"), value=''.join([f"``{alias}`` "
                                                                             for alias in _command.aliases]))

                if isinstance(_command, Group):
                    print(_command.commands)
                    subcommands = ""
                    for sc in _command.commands:
                        subcommands+="\n"+sc.name
                    embed.add_field(name=get_text("subcommands"), value=subcommands)



        await ctx.send(embed=embed)
    pass
