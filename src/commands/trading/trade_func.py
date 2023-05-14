"""
Copyright (C) 2022 William Redding - All Rights Reserved

See end of file for licence details
"""

import discord
from src.util import database
from src.lang.lang import get_locale_fm
from discord.ext.commands import Context
from datetime import datetime, timedelta


async def send_trade_notif_to_user(
    lang: str, sender: discord.Member, recipient: discord.Member
):
    trade = database.trade_requests.find_one(
        {"_id": sender.id, "recipient_id": recipient.id}
    )

    e = discord.Embed(
        title=get_locale_fm(lang, "trade_notif.title"), color=discord.Color.dark_theme()
    )
    e.set_thumbnail(url=sender.display_avatar.url)

    they_offer = create_item_str(lang, trade["sender_items"])
    for_your = create_item_str(lang, trade["recipient_items"])

    e.add_field(name=get_locale_fm(lang, "they_offer"), value=they_offer)
    e.add_field(name=get_locale_fm(lang, "for_your"), value=for_your)
    e.add_field(
        name=get_locale_fm(lang, "commands"),
        value=get_locale_fm(
            lang, "trade_notif.commands.value", sender.name, sender.name
        ),
        inline=False,
    )
    await recipient.send(embed=e)


def create_item_str(lang: str, items: list) -> str:
    if len(items) == 0:
        return get_locale_fm(lang, "none")
    else:
        string = ""
        for count, item in enumerate(items):
            item_data = database.item_data["items"][item["name"]]
            string += f"**{count+1})** `{item_data['formatted_name']}`\n"
        return string


async def send_trade_embed(lang: str, ctx: Context, trade: dict, incoming: bool):
    if incoming:
        user: discord.Member = await ctx.bot.fetch_user(trade["_id"])
        title = get_locale_fm(lang, "trade_embed.incoming_title", user.name)
    else:
        user: discord.Member = await ctx.bot.fetch_user(trade["recipient_id"])
        title = get_locale_fm(lang, "trade_embed.outgoing_title", user.name)

    e = discord.Embed(title=title, color=discord.Color.dark_theme())
    e.set_thumbnail(url=user.display_avatar.url)

    if incoming:
        your_items = create_item_str(lang, trade["recipient_items"])
        their_items = create_item_str(lang, trade["sender_items"])
    else:
        your_items = create_item_str(lang, trade["sender_items"])
        their_items = create_item_str(lang, trade["recipient_items"])

    e.add_field(name=get_locale_fm(lang, "they_offer"), value=their_items)
    e.add_field(name=get_locale_fm(lang, "for_your"), value=your_items)

    if not incoming:
        e.add_field(
            name=get_locale_fm(lang, "commands"),
            inline=False,
            value=get_locale_fm(lang, "trade_embed.commands.value", user.name),
        )

    time_left: timedelta = (
        trade["send_timestamp"] + timedelta(weeks=1)
    ) - datetime.utcnow()
    e.set_footer(
        text=get_locale_fm(
            lang,
            "trade_embed.footer",
            time_left.days,
            time_left.seconds // 3600,
            (time_left.seconds // 60) % 60,
        )
    )

    await ctx.send(embed=e)


async def send_trade_in_creation_embed(
    lang: str,
    ctx: Context,
    recipient: discord.Member,
    trade: dict = None,
    confirmed: bool = False,
):
    if confirmed:
        title = get_locale_fm(
            lang, "trade_in_creation_embed.sent.title", recipient.name
        )
    else:
        title = get_locale_fm(
            lang, "trade_in_creation_embed.unsent.title", recipient.name
        )

    e = discord.Embed(title=title)
    e.set_thumbnail(url=recipient.display_avatar.url)

    if confirmed:
        e.color = discord.Color.green()

    if trade is None:
        trade = database.trade_requests.find_one(
            {"_id": ctx.author.id, "send_timestamp": 0}
        )

        if trade is None:
            await ctx.send(get_locale_fm(lang, "no_trade_in_creation"))
            return

    your_items = create_item_str(lang, trade["sender_items"])
    their_items = create_item_str(lang, trade["recipient_items"])

    e.add_field(name=get_locale_fm(lang, "your_items"), value=your_items)
    e.add_field(name=get_locale_fm(lang, "their_items"), value=their_items)

    if not confirmed:
        e.add_field(
            name=get_locale_fm(lang, "commands"),
            value=get_locale_fm(lang, "trade_in_creation_embed.unsent.commands.value"),
            inline=False,
        )

    else:
        e.set_footer(text=get_locale_fm(lang, "trade_in_creation_embed.sent.footer"))

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
