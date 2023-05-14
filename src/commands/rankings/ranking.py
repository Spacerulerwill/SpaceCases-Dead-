"""
Copyright (C) 2022 William Redding - All Rights Reserved

See end of file for licence details
"""

import discord
from discord.ext.commands import Context
from src.util import database
from src.util.decorators import requires
from src.lang.lang import get_locale_fm
from src.util.embed_func import msg_embed


@requires(users_registered=True)
async def ranking(ctx: Context, type: str, user: discord.Member):
    if user is None:
        user = ctx.author

    user_data = database.user_data.find_one({"_id": user.id})
    lang = user_data["lang"]

    user_inv_value = sum(
        [
            database.item_data["items"][item["name"]]["price"]
            for item in user_data["inventory"]
        ]
    )

    position = 1

    if type == "global":
        leaderboard = list(database.leaderboards.find_one({"_id": "global"})["data"])
        text = get_locale_fm(lang, "ranking.global.text", user.name, position)
    elif type == "local":
        leaderboard = list(
            database.leaderboards.find_one({"_id": ctx.guild.id})["data"]
        )
        text = get_locale_fm(
            lang, "ranking.local.text", user.name, position, ctx.guild.name
        )

    for elem in leaderboard:
        _id, inv_value = elem

        if inv_value > user_inv_value:
            position += 1

    await msg_embed(ctx, text)


"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
