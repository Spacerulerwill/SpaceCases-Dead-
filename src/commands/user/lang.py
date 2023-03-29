import discord
from src.util import database
from src.util.decorators import requires
from src.util.embed_func import msg_embed
from src.util.lang import get_locale, supported_languages
from discord.ext.commands import Context

def get_lang_embed(lang:str) -> discord.Embed:
    return discord.Embed(
        description=get_locale(lang, "lang.current"),
        color=discord.Color.dark_theme()
    )

@requires(users_registered=True)
async def lang(ctx:Context, lang:str):
    user_data = database.user_data.find_one({"_id": ctx.author.id})
    if lang is None:
        await ctx.send(embed=get_lang_embed(user_data["lang"]))
        return
    
    # set new langauge
    lang = lang.lower().strip()

    if lang not in supported_languages:
        await msg_embed(ctx, get_locale(user_data["language"], "lang.not_found"))
        return
    
    database.user_data.update_one(
        {"_id": ctx.author.id},
        {
            "$set": {
                "lang": lang
            }
        }
    )

    await ctx.send(embed=get_lang_embed(lang))

