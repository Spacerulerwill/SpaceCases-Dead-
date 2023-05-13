"""
Copyright (C) 2022 William Redding - All Rights Reserved

See end of file for licence details
"""

import discord
from src.util import database
from src.lang.lang import get_locale_fm
from src.util.string_util import currency_str_format
from src.util.embed_func import msg_embed, msg_embed_edit, msg_embed_response
from src.util.decorators import requires
from discord.ext.commands import Context


@requires(users_registered=True)
async def sell(ctx: Context, item_index: int):
    user_data = database.user_data.find_one({"_id": ctx.author.id})
    lang = user_data["lang"]
    user_inventory = list(user_data["inventory"])

    if item_index > len(user_inventory):
        await msg_embed(
            ctx, get_locale_fm(lang, "inventory.not_found_index", item_index)
        )
        return

    # callbacks
    is_msg_deleted = False

    async def close_message():
        nonlocal is_msg_deleted
        if not is_msg_deleted:
            is_msg_deleted = True
            await msg.delete()

    async def sell_callback(interact: discord.Interaction):
        if interact.user.id != ctx.author.id:
            await msg_embed_response(
                interact.response,
                get_locale_fm(lang, "not_your_button"),
                ephemeral=True,
            )
            return

        update_result = database.user_data.update_one(
            {"_id": ctx.author.id, "inventory": {"name": item, "float": float}},
            {
                "$pull": {"inventory": {"name": item, "float": float}},
                "$inc": {
                    "balance": database.skin_data["skins"][item]["price"],
                    "inventory_size": -1,
                },
            },
        )

        if update_result.matched_count == 0:
            await close_message()
            await msg_embed(
                ctx, get_locale_fm(lang, "sell.item_missing", formatted_name)
            )
        else:
            await msg_embed_edit(
                msg, get_locale_fm(lang, "sell.success", formatted_name), view=None
            )

    async def cancel_callback(interact: discord.Interaction):
        if interact.user.id != ctx.author.id:
            await msg_embed_response(
                interact.response,
                get_locale_fm(lang, get_locale_fm("not_your_button")),
                ephemeral=True,
            )
            return

        await close_message()

    item_index -= 1

    item = user_inventory[item_index]["name"]
    float = user_inventory[item_index]["float"]
    item_data = database.skin_data["skins"][item]
    formatted_name = item_data["formatted_name"]
    price = currency_str_format(item_data["price"])

    view = discord.ui.View(timeout=30)
    view.on_timeout = close_message
    confirm_button = discord.ui.Button(
        label=get_locale_fm(lang, "button.sell"), style=discord.ButtonStyle.green
    )
    confirm_button.callback = sell_callback

    cancel_button = discord.ui.Button(
        label=get_locale_fm(lang, "button.cancel"), style=discord.ButtonStyle.red
    )
    cancel_button.callback = cancel_callback

    view.add_item(confirm_button)
    view.add_item(cancel_button)

    msg = await msg_embed(
        ctx, get_locale_fm(lang, "sell.are_you_sure", formatted_name, price), view=view
    )


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
