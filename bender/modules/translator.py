import typing

from discord.ext.commands import Cog, BucketType, command, cooldown
from googletrans import Translator

__all__ = ['GoogleTranslator']

from bender.utils.utils import BenderModule


@BenderModule
class GoogleTranslator(Cog, name = 'Google Translator'):
    def __init__(self, bot):
        self.bot = bot
        print(f"Initialized {str(__name__)}")

    @command(name="translate", aliases=["tr"])
    @cooldown(1, 10, BucketType.user)
    async def translate(self, ctx, lang: str, seclang: typing.Optional[str] = "", *,
                         content: typing.Optional[str] = ""):
        translator = Translator()
        destlang = "en"
        srclang = None
        if lang.startswith("("):
            if lang.endswith(")"):
                destlang = lang.replace("(", "").replace(")", "")
            else:
                await ctx.send("Syntax error!")
                return
            if seclang.startswith("("):
                if seclang.endswith(")"):
                    srclang = seclang.replace("(", "").replace(")", "")
                else:
                    await ctx.send("Syntax error")
            else:
                content = seclang + " " + content
        else:
            content = lang + " " + seclang + " " + content

        try:
            if srclang is None:
                product = translator.translate(content, dest=destlang)

            else:
                product = translator.translate(content, src=srclang, dest=destlang)
        except ValueError:
            await ctx.send("invalid_language_code")
            return
        await ctx.send("Translated from `" + product.src + "` as `" + product.text + "`")
