import discord
import asyncio
from discord.ext.commands import Context
from src.util import database
from src.lang.lang import get_locale_fm
from src.util.string_util import currency_str_format
from src.util.constants import LEADERBOARD_ELEMS_PER_PAGE
from src.util.embed_func import msg_embed


async def leaderboard(ctx: Context, type: str, page: int):
    user_data = database.user_data.find_one({"_id": ctx.author.id})

    if user_data is None:
        lang = "en"
    else:
        lang = user_data["lang"]

    page -= 1

    start = page * LEADERBOARD_ELEMS_PER_PAGE
    end = (page + 1) * LEADERBOARD_ELEMS_PER_PAGE

    if type == "global":
        data = list(database.leaderboards.find_one({"_id": "global"})["data"])[
            start:end
        ]
        embed_title = get_locale_fm(
            lang, "leaderboard.embed.global.title", start + 1, end
        )
        thumbnail = ctx.author.display_avatar.url
    elif type == "local":
        data = list(database.leaderboards.find_one({"_id": ctx.guild.id})["data"])[
            start:end
        ]
        embed_title = get_locale_fm(
            lang, "leaderboard.embed.local.title", ctx.guild.name, start + 1, end
        )
        if ctx.guild.icon is None:
            thumbnail = ctx.author.display_avatar.url
        else:
            thumbnail = ctx.guild.icon.url

    if len(data) == 0:
        await msg_embed(ctx, get_locale_fm(lang, "invalid_page"))
        return

    names = {}

    async def get_name(_id: int):
        nonlocal names
        user = ctx.guild.get_member(_id)

        if user is None:
            user = await ctx.bot.fetch_user(_id)

        names[_id] = user.name

    async with asyncio.TaskGroup() as tg:
        for _id, inv_value in data:
            tg.create_task(get_name(_id))

    string = ""
    for count, elem in enumerate(data):
        _id, inv_value = elem
        string += f"**{page * LEADERBOARD_ELEMS_PER_PAGE + count+1})** {names[_id]}: {currency_str_format(inv_value)}\n"

    e = discord.Embed(
        title=embed_title,
        description=string,
    )
    ctx.guild.icon
    e.set_thumbnail(url=thumbnail)
    e.set_footer(text=get_locale_fm(lang, "leaderboard.footer"))
    await ctx.send(embed=e)
