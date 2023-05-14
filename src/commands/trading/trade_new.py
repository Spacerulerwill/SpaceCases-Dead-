"""
Copyright (C) 2022 William Redding - All Rights Reserved

See end of file for licence details
"""

import discord
from discord.ext.commands import Context
from src.util import database
from src.lang.lang import get_locale_fm
from src.util.embed_func import msg_embed, msg_embed_response
from src.commands.trading.trade_func import send_trade_in_creation_embed
from pymongo.errors import DuplicateKeyError
from src.util.decorators import requires

from typing import Tuple


async def send_warning(lang: str, ctx: Context, recipient: discord.Member):
    e = discord.Embed(
        title=get_locale_fm(lang, "trade_new.warning.embed.footer"),
        description=get_locale_fm(lang, "trade_new.warning.embed.description"),
        color=discord.Color.red(),
    )
    e.set_thumbnail(url=ctx.author.display_avatar.url)
    e.set_footer(text=get_locale_fm(lang, "trade_new.warning.embed.footer"))

    # callback funcs
    async def view_timeout_callback():
        await close_message()

    async def close_message():
        try:
            await msg.delete()
        except discord.errors.NotFound:
            pass

    async def cancel_callback(interact: discord.Interaction):
        if interact.user.id != ctx.author.id:
            await msg_embed_response(
                interact.response,
                get_locale_fm(lang, "not_your_button"),
                ephemeral=True,
            )
            return

        await close_message()

    async def continue_callback(interact: discord.Interaction):
        if interact.user.id != ctx.author.id:
            await msg_embed_response(
                interact.response,
                get_locale_fm(lang, "not_your_button"),
                ephemeral=True,
            )
            return

        trade = {
            "_id": ctx.author.id,
            "send_timestamp": 0,
            "recipient_id": recipient.id,
            "sender_items": [],
            "recipient_items": [],
            "send_timestamp": 0,
        }
        database.trade_requests.update_one(
            {"_id": ctx.author.id, "send_timestamp": 0}, {"$set": trade}, upsert=True
        )

        await close_message()
        await send_trade_in_creation_embed(lang, ctx, recipient, trade)

    view = discord.ui.View(timeout=30)
    view.on_timeout = view_timeout_callback

    continue_button = discord.ui.Button(
        label=get_locale_fm(lang, "button.continue"), style=discord.ButtonStyle.green
    )
    continue_button.callback = continue_callback
    cancel_button = discord.ui.Button(
        label=get_locale_fm(lang, "button.cancel"), style=discord.ButtonStyle.red
    )
    cancel_button.callback = cancel_callback
    view.add_item(continue_button)
    view.add_item(cancel_button)

    msg = await ctx.send(embed=e, view=view)


def try_create_trade_request(
    ctx: Context, recipient: discord.Member
) -> Tuple[bool, dict]:
    trade = {
        "_id": ctx.author.id,
        "recipient_id": recipient.id,
        "sender_items": [],
        "recipient_items": [],
        "send_timestamp": 0,
    }
    update_result = database.trade_requests.update_one(
        {"_id": ctx.author.id, "send_timestamp": 0},
        {"$setOnInsert": trade},
        upsert=True,
    )

    return update_result.upserted_id is not None, trade


@requires(users_registered=True)
async def new(ctx: Context, recipient: discord.Member):
    lang = database.user_data.find_one({"_id": ctx.author.id})["lang"]

    try:
        successful, trade = try_create_trade_request(ctx, recipient)
    except DuplicateKeyError:
        await msg_embed(
            ctx,
            get_locale_fm(
                lang, "trade_error.already_have_trade_with_user", recipient.name
            ),
        )
        return

    if successful:
        # create new trade and show trade embed
        await send_trade_in_creation_embed(lang, ctx, recipient, trade)
    else:
        # show warning that this will override previous trade
        await send_warning(lang, ctx, recipient)


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
