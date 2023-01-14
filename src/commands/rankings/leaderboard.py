import discord
import asyncio
from discord.ext.commands import Context
from src.util import database
from src.util.string_util import currency_str_format
from src.util.constants import LEADERBOARD_ELEMS_PER_PAGE
from src.util.embed_func import msg_embed

async def leaderboard(ctx:Context, page:int):
    page -= 1
    data = database.leaderboard[page*LEADERBOARD_ELEMS_PER_PAGE:(page+1)*LEADERBOARD_ELEMS_PER_PAGE]

    if len(data) == 0:
        await msg_embed(ctx, "Invalid page number!")
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
    e = discord.Embed(title=f"Leaderboard - #{page * LEADERBOARD_ELEMS_PER_PAGE + 1} - {(page+1) * LEADERBOARD_ELEMS_PER_PAGE}", color=discord.Color.dark_theme(), description=string)
    e.set_thumbnail(url=ctx.bot.user.display_avatar.url)
    await ctx.send(embed=e)