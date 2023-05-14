"""
Copyright (C) 2022 William Redding - All Rights Reserved

See end of file for licence details
"""

import discord
from discord.ext.commands import Context
from src.util import database
from src.lang.lang import get_locale_fm
from src.util.decorators import requires
from src.util.string_util import currency_str_format
from src.util.embed_func import msg_embed
from decimal import Decimal


@requires(users_registered=True)
async def transfer(ctx: Context, member: discord.Member, amount: Decimal):
    lang = database.user_data.find_one({"_id": ctx.author.id})["lang"]

    if member is ctx.author:
        await msg_embed(ctx, get_locale_fm(lang, "transfer.cant_transfer_to_self"))
        return

    if amount <= 0:
        await msg_embed(ctx, get_locale_fm(lang, "transfer.amount_greater_than_0"))
        return

    # convert amount to cents
    amount = int(amount * Decimal("100"))

    # start a session to multi docuemnt atomic transaction
    with database.mongo_client.start_session() as session:
        with session.start_transaction():
            update_result = database.user_data.update_one(
                {"_id": ctx.author.id},
                [
                    {
                        "$set": {
                            "balance": {
                                "$cond": {
                                    "if": {"$gte": ["$balance", amount]},
                                    "then": {
                                        "$subtract": ["$balance", amount],
                                    },
                                    "else": "$balance",
                                }
                            },
                        }
                    }
                ],
                session=session,
            )

            if update_result.modified_count == 1:
                other_update_result = database.user_data.update_one(
                    {"_id": member.id}, {"$inc": {"balance": amount}}, session=session
                )
                if other_update_result.matched_count == 0:
                    await ctx.send(f"{member.name} is not registered!")
                    session.abort_transaction()
                    return

                await msg_embed(
                    ctx,
                    get_locale_fm(
                        lang,
                        "transfer.successfull",
                        currency_str_format(amount),
                        member.name,
                    ),
                )
            else:
                await msg_embed(ctx, get_locale_fm(lang, "transfer.insufficient_funds"))

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