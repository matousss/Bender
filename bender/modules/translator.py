import typing


from discord.ext.commands import Cog, BucketType, command, cooldown

import bender.utils.bender_utils
from bender.utils.message_handler import get_text

is_googletrans = True

try:
    # noinspection PyPackageRequirements
    import googletrans
except ImportError:
    is_googletrans = False


__all__ = ['GoogleTranslator']


@bender.utils.bender_utils.bender_module
class GoogleTranslator(Cog, name='Google Translator', description=get_text("cog_googletranslator_description")):
    def __init__(self, bot):
        if not is_googletrans:
            raise bender.utils.bender_utils.BenderModuleError(
                f"{self.__class__.__name__} requires googletrans package to work with")
        self.bot = bot
        print(f"Initialized {str(__name__)}")

    # todo revision
    @command(name="translate", aliases=["tr"], description=get_text("command_translate_description"),
             help=get_text("command_translate_help"), usage=f"[{{{get_text('source_language')}}} "
                                                            f"{{{get_text('destination_language')}}}] "
                                                            f"<{get_text('text_to_translate')}>")
    @cooldown(1, 10, BucketType.user)
    async def translate(self, ctx, lang: str, seclang: typing.Optional[str] = "", *,
                        content: typing.Optional[str] = ""):
        translator = googletrans.Translator()
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
