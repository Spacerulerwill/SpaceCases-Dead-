"""
Copyright (C) 2022 William Redding - All Rights Reserved

See end of file for licence details
"""

import discord
import random
import asyncio
import Levenshtein
from discord.ext.commands import Context
from src.util import database
from src.lang.lang import get_locale_fm
from src.util.decorators import requires
from src.util.embed_func import msg_embed
from src.util.string_util import remove_skin_name_formatting, currency_str_format

# GAME PRICES
SKIN_GAME_PRICE = 250
SKIN_GAME_REWARD = 750

SKIN_GAME_REWARD_STR = currency_str_format(SKIN_GAME_REWARD)


@requires(users_registered=True)
async def skin_game(ctx: Context):
    lang = database.user_data.find_one({"_id": ctx.author.id})["lang"]
    # check user has enough to play
    update_result = database.user_data.update_one(
        {"_id": ctx.author.id},
        [
            {
                "$set": {
                    "balance": {
                        "$cond": {
                            "if": {"$gte": ["$balance", SKIN_GAME_PRICE]},
                            "then": {"$subtract": ["$balance", SKIN_GAME_PRICE]},
                            "else": "$balance",
                        }
                    }
                }
            }
        ],
    )

    if update_result.modified_count == 0:
        await msg_embed(ctx, get_locale_fm(lang, "not_enough_funds"))
        return

    e = discord.Embed(
        title=get_locale_fm(lang, "skin_game.embed.title"),
        description=get_locale_fm(lang, "skin_game.embed.description"),
        color=discord.Color.dark_theme(),
    )

    random_item = random.choice(list(database.item_data["items"].keys()))
    random_item_data = database.item_data["items"][random_item]
    skin_name = remove_skin_name_formatting(
        random_item_data["formatted_name"].split(" | ")[1]
    ).strip()

    image_url = random_item_data["image_url"]

    e.set_image(url=image_url)

    await ctx.send(embed=e)

    def check(message: discord.Message):
        return message.author == ctx.author and message.channel == ctx.channel

    try:
        response: discord.Message = await ctx.bot.wait_for(
            "message", check=check, timeout=10
        )

        guess = response.content.strip().lower()

        if Levenshtein.ratio(guess, skin_name) > 0.8:
            await msg_embed(
                ctx, get_locale_fm(lang, "skin_game.won", SKIN_GAME_REWARD_STR)
            )
            database.user_data.update_one(
                {"_id": ctx.author.id}, {"$inc": {"balance": SKIN_GAME_REWARD}}
            )
        else:
            await msg_embed(
                ctx, get_locale_fm(lang, "skin_game.lost.incorrect_guess", skin_name)
            )

    except asyncio.TimeoutError:
        await msg_embed(
            ctx, get_locale_fm(lang, "skin_game.lost.out_of_time", skin_name)
        )

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