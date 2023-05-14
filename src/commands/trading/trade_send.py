"""
Copyright (C) 2022 William Redding - All Rights Reserved

See end of file for licence details
"""

import discord
from datetime import datetime
from discord.ext.commands import Context
from src.util import database
from src.lang.lang import get_locale_fm
from src.util.embed_func import msg_embed
from src.commands.trading.trade_func import (
    send_trade_in_creation_embed,
    send_trade_notif_to_user,
)
from src.util.decorators import requires


@requires(users_registered=True)
async def send(ctx: Context):
    lang = database.user_data.find_one({"_id": ctx.author.id})["lang"]
    trade = database.trade_requests.find_one(
        {"_id": ctx.author.id, "send_timestamp": 0}
    )
    if trade is None:
        await msg_embed(ctx, get_locale_fm(lang, "no_trade_in_creation"))
        return

    update_result = database.trade_requests.update_one(
        {"_id": ctx.author.id, "send_timestamp": 0},
        {"$set": {"send_timestamp": datetime.utcnow()}},
    )

    if update_result.matched_count == 0 or update_result.modified_count == 0:
        await msg_embed(ctx, get_locale_fm(lang, "no_trade_in_creation"))
        return

    recipient: discord.Member = await ctx.bot.fetch_user(trade["recipient_id"])
    await send_trade_notif_to_user(lang, ctx.author, recipient)
    await send_trade_in_creation_embed(lang, ctx, recipient, trade, True)

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