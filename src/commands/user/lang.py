import discord
from src.util import database
from src.util.decorators import requires
from src.lang.lang import get_locale_fm, supported_languages, supported_languages_str
from discord.ext.commands import Context


def get_lang_embed(lang: str) -> discord.Embed:
    e = discord.Embed(
        description=get_locale_fm(lang, "lang.current"),
        color=discord.Color.dark_theme(),
    )
    e.add_field(
        name=get_locale_fm(lang, "lang.embed.supported_languages"),
        value=supported_languages_str,
    )
    return e


@requires(users_registered=True)
async def lang(ctx: Context, lang: str):
    user_data = database.user_data.find_one({"_id": ctx.author.id})
    if lang is None:
        await ctx.send(embed=get_lang_embed(user_data["lang"]))
        return

    # set new langauge
    lang = lang.lower().strip()

    if lang not in supported_languages:
        e = discord.Embed(
            description=get_locale_fm(user_data["lang"], "lang.not_found")
        )
        e.add_field(
            name=get_locale_fm(user_data["lang"], "lang.embed.supported_languages"),
            value=supported_languages_str,
        )

        await ctx.send(embed=e)
        return

    database.user_data.update_one({"_id": ctx.author.id}, {"$set": {"lang": lang}})

    await ctx.send(embed=get_lang_embed(lang))