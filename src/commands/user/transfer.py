"""
Copyright (C) 2022 William Redding - All Rights Reserved

See end of file for licence details
"""

import discord
from discord.ext.commands import Context
from src.util import database
from src.lang.lang import get_locale_fm
from src.util.decorators import requires
from src.util.string_util import currency_str_format
from src.util.embed_func import msg_embed
from decimal import Decimal


@requires(users_registered=True)
async def transfer(ctx: Context, member: discord.Member, amount: Decimal):
    lang = database.user_data.find_one({"_id": ctx.author.id})["lang"]

    if member is ctx.author:
        await msg_embed(ctx, get_locale_fm(lang, "transfer.cant_transfer_to_self"))
        return

    if amount <= 0:
        await msg_embed(ctx, get_locale_fm(lang, "transfer.amount_greater_than_0"))
        return

    # convert amount to cents
    amount = int(amount * Decimal("100"))

    # start a session to multi docuemnt atomic transaction
    with database.mongo_client.start_session() as session:
        with session.start_transaction():
            update_result = database.user_data.update_one(
                {"_id": ctx.author.id},
                [
                    {
                        "$set": {
                            "balance": {
                                "$cond": {
                                    "if": {"$gte": ["$balance", amount]},
                                    "then": {
                                        "$subtract": ["$balance", amount],
                                    },
                                    "else": "$balance",
                                }
                            },
                        }
                    }
                ],
                session=session,
            )

            if update_result.modified_count == 1:
                other_update_result = database.user_data.update_one(
                    {"_id": member.id}, {"$inc": {"balance": amount}}, session=session
                )
                if other_update_result.matched_count == 0:
                    await ctx.send(f"{member.name} is not registered!")
                    session.abort_transaction()
                    return

                await msg_embed(
                    ctx,
                    get_locale_fm(
                        lang,
                        "transfer.successfull",
                        currency_str_format(amount),
                        member.name,
                    ),
                )
            else:
                await msg_embed(ctx, get_locale_fm(lang, "transfer.insufficient_funds"))


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
