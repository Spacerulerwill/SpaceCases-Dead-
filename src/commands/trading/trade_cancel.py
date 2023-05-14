"""
Copyright (C) 2022 William Redding - All Rights Reserved

See end of file for licence details
"""

import discord
from discord.ext.commands import Context
from src.util import database
from src.lang.lang import get_locale_fm
from src.util.decorators import requires
from src.util.embed_func import msg_embed


@requires(users_registered=True)
async def cancel(ctx: Context, recipient: discord.Member):
    lang = database.user_data.find_one({"_id": ctx.author.id})["lang"]
    # if recipient is None cancel the current trade in creation
    if recipient is None:
        delete_result = database.trade_requests.delete_one(
            {"_id": ctx.author.id, "send_timestamp": 0}
        )
        successful = delete_result.deleted_count >= 1

        if successful:
            await msg_embed(ctx, get_locale_fm(lang, "trade_cancel.cancelled_current"))
        else:
            await msg_embed(ctx, get_locale_fm(lang, "no_trade_in_creation"))

    else:  # if a recipient is provided trade to that user
        delete_result = database.trade_requests.delete_one(
            {"_id": ctx.author.id, "recipient_id": recipient.id}
        )
        successful = delete_result.deleted_count >= 1

        if successful:
            await msg_embed(
                ctx,
                get_locale_fm(
                    lang, "trade_cancel.cancelled_trade_to_user", recipient.name
                ),
            )
        else:
            await msg_embed(
                ctx, get_locale_fm(lang, "no_outgoing_trade", recipient.name)
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