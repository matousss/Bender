from discord.ext.commands import Context


async def can_join_speak(ctx: Context):
    return ctx.me.guild_permissions.speak and ctx.me.guild_permissions.connect
