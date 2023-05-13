"""
Copyright (C) 2022 William Redding - All Rights Reserved

See end of file for licence details
"""

import discord
import asyncio
from datetime import datetime, timedelta
from discord.ext.commands import Context
from src.util import database
from src.lang.lang import get_locale_fm
from src.util.constants import MAX_TRADES_PER_PAGE
from src.util.embed_func import msg_embed, msg_embed_response
from src.util.decorators import requires


@requires(users_registered=True)
async def trades(ctx: Context, in_out: str, page: int):
    lang = database.user_data.find_one({"_id": ctx.author.id})["lang"]

    if in_out is None:
        in_out = "all"
    if page is None:
        page = 1
    elif page < 1:
        await msg_embed(ctx, get_locale_fm(lang, "invalid_page"))
        return

    if in_out == "all":
        title = get_locale_fm(lang, "trades.all.embed.title")
        trades = list(
            database.trade_requests.find(
                {
                    "$or": [
                        {"_id": ctx.author.id, "send_timestamp": {"$ne": 0}},
                        {"recipient_id": ctx.author.id, "send_timestamp": {"$ne": 0}},
                    ]
                }
            )
        )
    elif in_out == "in":
        title = get_locale_fm(lang, "trades.in.embed.title")
        trades = list(
            database.trade_requests.find(
                {"recipient_id": ctx.author.id, "send_timestamp": {"$ne": 0}}
            )
        )
    elif in_out == "out":
        title = get_locale_fm(lang, "trades.out.embed.title")
        trades = list(
            database.trade_requests.find(
                {"_id": ctx.author.id, "send_timestamp": {"$ne": 0}}
            )
        )

    trades_pages = [
        trades[x : x + MAX_TRADES_PER_PAGE]
        for x in range(0, len(trades), MAX_TRADES_PER_PAGE)
    ]

    if len(trades) == 0:
        num_pages = 1
        page = 0
    else:
        num_pages = len(trades_pages)
        page -= 1

    async def get_trades_embed() -> discord.Embed:
        nonlocal num_pages, page

        if len(trades) == 0:
            trade_list_str = get_locale_fm(lang, "none")
        else:
            try:
                current_trade_page = trades_pages[page]
            except IndexError:
                await msg_embed(ctx, get_locale_fm(lang, "invalid_page"))
                return

            trade_list_str = ""

            id_name_dict = {}

            async def get_name(_id: int):
                nonlocal id_name_dict
                user = ctx.guild.get_member(_id)

                if user is None:
                    user = await ctx.bot.fetch_user(_id)

                id_name_dict[_id] = user.name

            if in_out == "all":
                async with asyncio.TaskGroup() as tg:
                    for trade in current_trade_page:
                        if trade["_id"] == ctx.author.id:
                            tg.create_task(get_name(trade["recipient_id"]))
                        elif trade["recipient_id"] == ctx.author.id:
                            tg.create_task(get_name(trade["_id"]))

                for trade in current_trade_page:
                    time_left: timedelta = (trade["send_timestamp"] + one_week) - now

                    if trade["_id"] == ctx.author.id:
                        recipient = id_name_dict[trade["recipient_id"]]
                        trade_list_str += get_locale_fm(
                            lang, "trades.outgoing_to", recipient, time_left.days
                        )
                    elif trade["recipient_id"] == ctx.author.id:
                        sender = id_name_dict[trade["_id"]]
                        trade_list_str += get_locale_fm(
                            lang, "trades.incoming_from", sender, time_left.days
                        )

            elif in_out == "in":
                async with asyncio.TaskGroup() as tg:
                    for trade in current_trade_page:
                        tg.create_task(get_name(trade["_id"]))

                for trade in current_trade_page:
                    time_left: timedelta = (trade["send_timestamp"] + one_week) - now
                    sender = id_name_dict[trade["_id"]]
                    trade_list_str += get_locale_fm(
                        lang, "trades.incoming_from", sender, time_left.days
                    )

            elif in_out == "out":
                async with asyncio.TaskGroup() as tg:
                    for trade in current_trade_page:
                        tg.create_task(get_name(trade["recipient_id"]))

                for trade in current_trade_page:
                    time_left: timedelta = (trade["send_timestamp"] + one_week) - now
                    recipient = id_name_dict[trade["recipient_id"]]
                    trade_list_str += get_locale_fm(
                        lang, "trades.outgoing_to", recipient, time_left.days
                    )

        e = discord.Embed(title=title, color=discord.Color.dark_theme())
        e.set_thumbnail(url=ctx.author.display_avatar.url)
        e.add_field(
            name=get_locale_fm(
                lang, "trades.embed.trade_list", len(trades), page + 1, num_pages
            ),
            value=trade_list_str,
        )
        e.add_field(
            name="Commands",
            value=get_locale_fm(
                lang,
                "trades.embed.commands.value",
            ),
            inline=False,
        )

        return e

    # if more than one page, create view
    async def next_callback(interact: discord.Interaction):
        if interact.user.id != ctx.author.id:
            await msg_embed_response(
                interact.response,
                get_locale_fm(lang, "not_your_button"),
                ephemeral=True,
            )
            return

        nonlocal page

        if page < num_pages - 1:
            page += 1
        else:
            page = 0

        await interact.response.edit_message(embed=await get_trades_embed())

    async def prev_callback(interact: discord.Interaction):
        if interact.user.id != ctx.author.id:
            await msg_embed_response(
                interact.response,
                get_locale_fm(lang, "not_your_button"),
                ephemeral=True,
            )
            return

        nonlocal page

        if page > 0:
            page -= 1
        else:
            page = num_pages - 1

        await interact.response.edit_message(embed=await get_trades_embed())

    async def view_timeout_callback():
        await msg.delete()

    view = None
    if num_pages > 1:
        view = discord.ui.View()
        view.on_timeout = view_timeout_callback
        prev_button = discord.ui.Button(label="◀", style=discord.ButtonStyle.gray)
        prev_button.callback = prev_callback
        next_button = discord.ui.Button(label="▶", style=discord.ButtonStyle.gray)
        next_button.callback = next_callback
        view.add_item(prev_button)
        view.add_item(next_button)

    now = datetime.utcnow()
    one_week = timedelta(weeks=1)
    msg = await ctx.send(embed=await get_trades_embed(), view=view)


"""
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.

                            Preamble

  The GNU General Public License is a free, copyleft license for
software and other kinds of works.

  The licenses for most software and other practical works are designed
to take away your freedom to share and change the works.  By contrast,
the GNU General Public License is intended to guarantee your freedom to
share and change all versions of a program--to make sure it remains free
software for all its users.  We, the Free Software Foundation, use the
GNU General Public License for most of our software; it applies also to
any other work released this way by its authors.  You can apply it to
your programs, too.

  When we speak of free software, we are referring to freedom, not
price.  Our General Public Licenses are designed to make sure that you
have the freedom to distribute copies of free software (and charge for
them if you wish), that you receive source code or can get it if you
want it, that you can change the software or use pieces of it in new
free programs, and that you know you can do these things.

  To protect your rights, we need to prevent others from denying you
these rights or asking you to surrender the rights.  Therefore, you have
certain responsibilities if you distribute copies of the software, or if
you modify it: responsibilities to respect the freedom of others.

  For example, if you distribute copies of such a program, whether
gratis or for a fee, you must pass on to the recipients the same
freedoms that you received.  You must make sure that they, too, receive
or can get the source code.  And you must show them these terms so they
know their rights.

  Developers that use the GNU GPL protect your rights with two steps:
(1) assert copyright on the software, and (2) offer you this License
giving you legal permission to copy, distribute and/or modify it.

  For the developers' and authors' protection, the GPL clearly explains
that there is no warranty for this free software.  For both users' and
authors' sake, the GPL requires that modified versions be marked as
changed, so that their problems will not be attributed erroneously to
authors of previous versions.

  Some devices are designed to deny users access to install or run
modified versions of the software inside them, although the manufacturer
can do so.  This is fundamentally incompatible with the aim of
protecting users' freedom to change the software.  The systematic
pattern of such abuse occurs in the area of products for individuals to
use, which is precisely where it is most unacceptable.  Therefore, we
have designed this version of the GPL to prohibit the practice for those
products.  If such problems arise substantially in other domains, we
stand ready to extend this provision to those domains in future versions
of the GPL, as needed to protect the freedom of users.

  Finally, every program is threatened constantly by software patents.
States should not allow patents to restrict development and use of
software on general-purpose computers, but in those that do, we wish to
avoid the special danger that patents applied to a free program could
make it effectively proprietary.  To prevent this, the GPL assures that
patents cannot be used to render the program non-free.

  The precise terms and conditions for copying, distribution and
modification follow.
"""
