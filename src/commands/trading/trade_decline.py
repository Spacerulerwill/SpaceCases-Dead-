"""
Copyright (C) 2022 William Redding - All Rights Reserved

See end of file for licence details
"""

import discord
from src.util import database
from src.lang.lang import get_locale_fm
from discord.ext.commands import Context
from src.commands.trading.trade_func import create_item_str
from src.util.decorators import requires
from src.util.embed_func import msg_embed


@requires(users_registered=True)
async def decline(ctx: Context, sender: discord.Member):
    lang = database.user_data.find_one({"_id": ctx.author.id})["lang"]
    deleted_document = database.trade_requests.find_one_and_delete(
        {"_id": sender.id, "recipient_id": ctx.author.id, "send_timestamp": {"$ne": 0}}
    )

    if deleted_document is None:
        await msg_embed(ctx, get_locale_fm(lang, "no_incoming_trade", sender.name))
    else:
        # inform recipient trade has been declined
        e = discord.Embed(
            title=get_locale_fm(
                lang, "trade_decline.author_embed.description", sender.name
            ),
            color=discord.Color.red(),
        )

        await msg_embed(ctx, embed=e)

        # inform original sender that their request was declined
        e = discord.Embed(
            title=get_locale_fm(
                lang, "trade_decline.sender_embed.title", ctx.author.name
            ),
            color=discord.Color.red(),
        )
        e.set_thumbnail(url=sender.display_avatar.url)

        you_wanted = create_item_str(lang, deleted_document["recipient_items"])
        for_your = create_item_str(lang, deleted_document["sender_items"])
        e.add_field(name=get_locale_fm(lang, "you_wanted"), value=you_wanted)
        e.add_field(name=get_locale_fm(lang, "for_your"), value=for_your)
        await sender.send(embed=e)

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