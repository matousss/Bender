import typing

from discord.ext.commands import BucketType, command, cooldown

import bender.utils.bender_utils
from bender.bot import Bender as Bot, BenderCog

is_googletrans = True

try:
    # noinspection PyPackageRequirements
    import googletrans
except ImportError:
    is_googletrans = False

__all__ = ['GoogleTranslator']


def setup(bot: Bot):
    bot.add_cog(GoogleTranslator(bot))


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


class GoogleTranslator(BenderCog, name='Google Translator', description="cog_googletranslator_description"):
    def __init__(self, bot: Bot):
        if not is_googletrans:
            raise bender.utils.bender_utils.BenderModuleError(
                f"{self.__class__.__name__} requires googletrans package to work with")

        super().__init__(bot)

    # todo revision
    @command(name="translate", aliases=["tr"], description="command_translate_description",
             usage="command_translate_usage")
    @cooldown(1, 2, BucketType.user)
    async def translate(self, ctx, lang: str, seclang: typing.Optional[str] = "", *,
                        content: typing.Optional[str] = ""):
        translator = googletrans.Translator()
        destlang = "en"
        srclang = None
        if lang.startswith("{"):
            if lang.endswith("}"):
                destlang = lang.replace("{", "").replace("}", "")
            else:
                await ctx.send(self.get_text("%s invalid_argument") % f"``{destlang}``")
                return
            if seclang.startswith("{"):
                if seclang.endswith("}"):
                    srclang = seclang.replace("{", "").replace("}", "")
                else:
                    await ctx.send(self.get_text("%s invalid_argument") % f"``{seclang}``")
            else:
                content = seclang + " " + content
        else:
            content = lang + " " + seclang + " " + content
        if len(content) > 1000:
            await ctx.send(self.get_text('message_too_long'))

        if srclang is None:
            try:
                product = translator.translate(content, dest=destlang)
            except ValueError:
                await ctx.send(self.get_text("%s translate_error_invalid_code") % f"``{destlang}``")
                return
        else:
            try:
                product = translator.translate(content, src=srclang, dest=destlang)
            except ValueError:
                await ctx.send(self.get_text("translate_error_invalid_code"))
                return
        await ctx.send(f"{self.get_text('translated_from')} `{product.src}` {self.get_text('as')} `{product.text}`")
