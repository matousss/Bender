import typing

from discord.ext.commands import Cog, BucketType, command, cooldown
from googletrans import Translator

__all__ = ['GoogleTranslator']

from bender.utils.bender_utils import bender_module
from bender.utils.message_handler import get_text

@bender_module
class GoogleTranslator(Cog, name = 'Google Translator', description = get_text("cog_googletranslator_description")):
    def __init__(self, bot):
        self.bot = bot
        print(f"Initialized {str(__name__)}")

    #todo revision
    @command(name="translate", aliases=["tr"], description=get_text("command_translate_description"),
                      help=get_text("command_translate_help"))
    @cooldown(1, 10, BucketType.user)
    async def translate(self, ctx, lang: str, seclang: typing.Optional[str] = "", *,
                         content: typing.Optional[str] = ""):
        translator = Translator()
        destlang = "en"
        srclang = None
        if lang.startswith("{"):
            if lang.endswith("}"):
                destlang = lang.replace("{", "").replace("}", "")
            else:
                await ctx.send(get_text("%s invalid_argument") % destlang)
                return
            if seclang.startswith("{"):
                if seclang.endswith("}"):
                    srclang = seclang.replace("{", "").replace("}", "")
                else:
                    await ctx.send(get_text("%s invalid_argument") % seclang)
            else:
                content = seclang + " " + content
        else:
            content = lang + " " + seclang + " " + content


        if srclang is None:
            try:
                product = translator.translate(content, dest=destlang)
            except ValueError:
                await ctx.send(get_text("%s translate_error_invalid_code") % destlang)
                return
        else:
            try:
                product = translator.translate(content, src=srclang, dest=destlang)
            except ValueError:
                await ctx.send(get_text("translate_error_invalid_code"))
                return
        await ctx.send(f"{get_text('translated_from')} `{product.src}` {get_text('as')} `{product.text}`")
