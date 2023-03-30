import discord
from discord.ext.commands import Context
from src.util import database
from src.util.decorators import requires
from src.util.lang import get_locale
from src.util.embed_func import msg_embed


@requires(users_registered=True)
async def ranking(ctx: Context, user: discord.Member):
    if user is None:
        user = ctx.author

    user_data = database.user_data.find_one({"_id": user.id})
    lang = user_data["lang"]

    user_inv_value = sum(
        [
            database.skin_data["skins"][item["name"]]["price"]
            for item in user_data["inventory"]
        ]
    )

    position = 1
    for elem in database.leaderboard:
        _id, inv_value = elem

        if inv_value > user_inv_value:
            position += 1

    await msg_embed(ctx, get_locale(lang, "ranking.text", user.name, position))
