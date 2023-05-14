"""
Copyright (C) 2022 William Redding - All Rights Reserved

See end of file for licence details
"""

from discord.ext.commands import Context
from src.util import database
from src.lang.lang import get_locale_fm
from src.util.embed_func import msg_embed
import time


async def register(ctx: Context):
    update_result = database.user_data.update_one(
        {"_id": ctx.author.id},
        {
            "$setOnInsert": {
                "join_date": int(time.time()),
                "balance": 0,
                "lang": "en",
                "last_claim": 0,
                "claim_streak": 0,
                "inventory": [],
                "inventory_size": 0,
                "inventory_max_capacity": 5,
                "stats": {
                    "containers_opened": 0,
                    "total_spent": 0,
                    "total_return": 0,
                },
            }
        },
        upsert=True,
    )

    user_data = database.user_data.find_one({"_id": ctx.author.id})
    if update_result.upserted_id == None:
        await msg_embed(
            ctx, get_locale_fm(user_data["lang"], "register.already_registered")
        )
    else:
        await msg_embed(ctx, get_locale_fm(user_data["lang", "register.success"]))

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