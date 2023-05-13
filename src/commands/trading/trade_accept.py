"""
Copyright (C) 2022 William Redding - All Rights Reserved

See end of file for licence details
"""

import discord
from src.util import database
from src.commands.trading.trade_func import create_item_str
from discord.ext.commands import Context
from src.util.embed_func import msg_embed
from src.lang.lang import get_locale_fm
from src.util.decorators import requires


@requires(users_registered=True)
async def accept(ctx: Context, sender: discord.Member):
    lang = database.user_data.find_one({"_id": ctx.author.id})["lang"]

    with database.mongo_client.start_session() as session:
        with session.start_transaction():
            trade = database.trade_requests.find_one(
                {
                    "_id": sender.id,
                    "recipient_id": ctx.author.id,
                    "send_timestamp": {"$ne": 0},
                },
                session=session,
            )

            if trade is None:
                await msg_embed(
                    ctx, get_locale_fm(lang, "no_incoming_trade", sender.name)
                )
                session.abort_transaction()
                return

            # check items are in both users inventories
            sender_data = database.user_data.find_one({"_id": sender.id})
            recipient_data = database.user_data.find_one({"_id": ctx.author.id})

            sender_items_missing = []
            recipient_items_missing = []

            for item in trade["sender_items"]:
                if item not in sender_data["inventory"]:
                    sender_items_missing.append(item)

            for item in trade["recipient_items"]:
                if item not in recipient_data["inventory"]:
                    recipient_items_missing.append(item)

            if len(sender_items_missing) == 0 and len(recipient_items_missing) == 0:
                # no missing items, next check that the trade will not result in inventory capacity overflow
                if (
                    sender_data["inventory_size"] + len(trade["sender_items"])
                    > sender_data["inventory_capacity"]
                ):
                    e = discord.Embed(
                        title=get_locale_fm(lang, "trade_error"),
                        description=get_locale_fm(
                            lang, "trade_error.author_not_enough_space", sender.name
                        ),
                        color=discord.Color.red(),
                    )
                    await ctx.send(embed=e)
                    return

                if (
                    recipient_data["inventory_size"] + len(trade["recipient_items"])
                    > sender_data["inventory_capacity"]
                ):
                    e = discord.Embed(
                        title=get_locale_fm(lang, "trade_error"),
                        description=get_locale_fm(
                            lang,
                            "trade_error.sender_not_enough_space",
                            sender.name,
                            sender.name,
                        ),
                        color=discord.Color.red(),
                    )
                    await ctx.send(embed=e)
                    return

                # delete trade document - no longer needed
                database.trade_requests.delete_one(
                    {
                        "_id": sender.id,
                        "recipient_id": ctx.author.id,
                        "send_timestamp": {"$ne": 0},
                    },
                    session=session,
                )

                # swap items round
                database.user_data.update_one(
                    {"_id": ctx.author.id},
                    {
                        "$pull": {"inventory": {"$in": trade["recipient_items"]}},
                        "$inc": {"inventory_size" - len(trade["recipient_items"])},
                    },
                    session=session,
                )
                database.user_data.update_one(
                    {"_id": ctx.author.id},
                    {
                        "$push": {"inventory": {"$each": trade["sender_items"]}},
                        "$inc": {"inventory_size": len(trade["sender_items"])},
                    },
                    session=session,
                )
                database.user_data.update_one(
                    {"_id": sender.id},
                    {
                        "$pull": {"inventory": {"$in": trade["sender_items"]}},
                        "$inc": {"inventory_size": -len(trade["sender_items"])},
                    },
                    session=session,
                )
                database.user_data.update_one(
                    {"_id": sender.id},
                    {
                        "$push": {"inventory": {"$each": trade["recipient_items"]}},
                        "$inc": {"inventory_size": len(trade["recipient_items"])},
                    },
                    session=session,
                )

                # send embed to perso n who accepted
                recipient_embed = discord.Embed(
                    title=get_locale_fm(
                        lang, "trade_accept.author_embed.description", sender.name
                    ),
                    color=discord.Color.green(),
                )
                recipient_embed.add_field(
                    name="Your New Items",
                    value=create_item_str(lang, trade["sender_items"]),
                )
                recipient_embed.set_thumbnail(url=ctx.author.display_avatar.url)

                await ctx.send(embed=recipient_embed)

                # inform the original sender that it was accepted
                sender_embed = discord.Embed(
                    title=get_locale_fm(
                        lang, "trade_accept.sender_embed.title", ctx.author.name
                    ),
                    color=discord.Color.green(),
                )
                sender_embed.add_field(
                    name=get_locale_fm(lang, "your_new_items"),
                    value=create_item_str(lang, trade["recipient_items"]),
                )
                recipient_embed.set_thumbnail(url=sender.display_avatar.url)

                await sender.send(embed=sender_embed)

            else:
                # items missing, cancel and inform participants that cannot perform trade!
                database.trade_requests.delete_one(
                    {
                        "_id": sender.id,
                        "recipient_id": ctx.author.id,
                        "send_timestamp": {"$ne": 0},
                    },
                    session=session,
                )

                # send message to recipient
                e = discord.Embed(
                    title=get_locale_fm(lang, "trade_error"),
                    description=get_locale_fm(
                        lang, "trade_error.missing_items", sender.name
                    ),
                    color=discord.Color.red(),
                )
                e.set_thumbnail(url=ctx.author.display_avatar.url)

                e.add_field(
                    name=get_locale_fm(lang, "you_are_missing"),
                    value=create_item_str(lang, recipient_items_missing),
                )
                e.add_field(
                    name=get_locale_fm(lang, "sender_is_missing", sender.name),
                    value=create_item_str(lang, sender_items_missing),
                )

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
