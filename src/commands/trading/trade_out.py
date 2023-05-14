"""
Copyright (C) 2022 William Redding - All Rights Reserved

See end of file for licence details
"""

import discord
from src.util import database
from src.lang.lang import get_locale_fm
from src.util.embed_func import msg_embed
from discord.ext.commands import Context
from src.commands.trading.trade_func import send_trade_embed
from src.util.decorators import requires


@requires(users_registered=True)
async def view_outgoing_trade(ctx: Context, recipient: discord.Member):
    lang = database.user_data.find_one({"_id": ctx.author.id})["lang"]
    trade = database.trade_requests.find_one(
        {
            "_id": ctx.author.id,
            "recipient_id": recipient.id,
            "send_timestamp": {"$ne": 0},
        }
    )

    if trade is None:
        await msg_embed(ctx, get_locale_fm(lang, "no_incoming_trade", recipient.name))
        return

    await send_trade_embed(lang, ctx, trade, False)


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
