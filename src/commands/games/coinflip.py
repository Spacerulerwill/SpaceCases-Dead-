"""
Copyright (C) 2022 William Redding - All Rights Reserved

See end of file for licence details
"""

import discord
import random
from discord.ext.commands import Context
from src.util.images import CT_LOGO, T_LOGO
from src.util.embed_func import msg_embed
from src.util.string_util import currency_str_format
from src.lang.lang import get_locale_fm
from src.util.decorators import requires
from src.util import database
from decimal import Decimal


@requires(users_registered=True)
async def coinflip(ctx: Context, t_ct: str, amount: Decimal):
    lang = database.user_data.find_one({"_id": ctx.author.id})["lang"]
    integer_amount = int(amount * Decimal("100"))

    if integer_amount <= 0:
        await msg_embed(ctx, get_locale_fm(lang, "greater_than_0"))
        return

    if random.random() < 0.5:
        winner = "t"
        url = T_LOGO
    else:
        winner = "ct"
        url = CT_LOGO

    if t_ct == winner:
        # they won!
        update_result = database.user_data.update_one(
            {"_id": ctx.author.id},
            [
                {
                    "$set": {
                        "balance": {
                            "$cond": {
                                "if": {"$gte": ["$balance", integer_amount]},
                                "then": {"$add": ["$balance", integer_amount]},
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
            title=get_locale_fm(
                lang, "coinflip.win.embed.title", currency_str_format(integer_amount)
            ),
            color=discord.Color.green(),
        )

    else:
        update_result = database.user_data.update_one(
            {"_id": ctx.author.id},
            [
                {
                    "$set": {
                        "balance": {
                            "$cond": {
                                "if": {"$gte": ["$balance", integer_amount]},
                                "then": {"$subtract": ["$balance", integer_amount]},
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

        # they lost
        e = discord.Embed(
            title=get_locale_fm(
                lang, "coinflip.loss.embed.title", currency_str_format(integer_amount)
            ),
            color=discord.Color.red(),
        )

        e.set_footer(
            text=get_locale_fm(lang, "coinflip.loss.embed.description"),
            icon_url=ctx.author.display_avatar.url,
        )

    e.set_image(url=url)

    await ctx.send(embed=e)


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
