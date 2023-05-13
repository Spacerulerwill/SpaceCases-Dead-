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
            item_data = database.skin_data["skins"][item["name"]]
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
