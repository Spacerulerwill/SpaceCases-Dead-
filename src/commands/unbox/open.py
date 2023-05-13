"""
Copyright (C) 2022 William Redding - All Rights Reserved

See end of file for licence details
"""

import discord
import random
from discord.ext.commands import Context
from src.util import database
from src.lang.lang import get_locale_fm
from src.util.decorators import requires
from src.util.constants import KEY_PRICE, rarity_color_dict
from src.util.string_util import (
    currency_str_format,
    get_closest_match,
    get_inspect_link_3D,
)
from src.util.item_func import gen_item, get_item_embed
from src.util.embed_func import msg_embed, msg_embed_response


@requires(room=True, users_registered=True)
async def open(ctx: Context, *args):
    container_name = " ".join(args[:]).strip().lower()

    user_data = database.user_data.find_one({"_id": ctx.author.id})
    lang = user_data["lang"]

    # check case exists
    try:
        container_data = database.containers[container_name]
        container_price = container_data["price"]

        # souvenir packages dont require keys
        if container_data["type"] != "souvenir_package":
            container_price += KEY_PRICE

    except KeyError:
        # try and find closest match
        closest_match = get_closest_match(container_name, database.containers.keys())

        # if match is reasonably close enough
        if closest_match is None:
            await msg_embed(ctx, get_locale_fm(lang, "container.not_found"))
        else:
            container_data = database.containers[closest_match]
            await msg_embed(
                ctx,
                get_locale_fm(lang, "container.not_found_suggest", closest_match),
            )
        return

    # check user has enough balance for case
    if user_data["balance"] < container_price:
        await msg_embed(ctx, get_locale_fm(lang, "not_enough_funds"))
        return

    # select skin rarity
    rarity_rand = random.random()
    case_odds: dict = container_data["odds"]
    for key, value in case_odds.items():
        if rarity_rand > value:
            rarity = key
            break

    skin_pool = container_data["items"][rarity]
    chosen_item = random.choice(skin_pool)

    # get the item dict
    item = gen_item(chosen_item, container_data["type"])

    item_data = database.skin_data["skins"][item["name"]]
    e = get_item_embed(lang, item_data)

    # if its a weapon, add float field
    if container_data["type"] in ["case", "souvenir_package"]:
        e.add_field(name=get_locale_fm(lang, "float"), value=str(item["float"]))

    e.set_footer(text=get_locale_fm(lang, "open.embed.footer"))

    interacted_with = False

    # decrement balance, increment total spent, increase total return and containers opened
    database.user_data.update_one(
        {"_id": ctx.author.id},
        {
            "$inc": {
                "balance": -(container_price),
                "stats.total_spent": container_price,
                "stats.total_return": item_data["price"],
                "stats.containers_opened": 1,
            }
        },
    )

    # callbacks
    async def sell_item():
        # change color to dark gray, remove footer, change balance to have balance of skin
        database.user_data.update_one(
            {"_id": ctx.author.id}, {"$inc": {"balance": item_data["price"]}}
        )

        e.colour = discord.colour.Color.dark_gray()
        e.set_footer(text="")

        await msg.edit(embed=e, view=None)

    async def sell_callback(interact: discord.Interaction):
        if ctx.author.id != interact.user.id:
            await msg_embed_response(
                interact.response,
                get_locale_fm(lang, "not_your_button"),
                ephemeral=True,
            )
            return

        nonlocal interacted_with

        if not interacted_with:
            interacted_with = True
            await sell_item()
        else:
            await interact.response.defer()

    async def inventory_callback(interact: discord.Interaction):
        if ctx.author.id != interact.user.id:
            await msg_embed_response(
                interact.response,
                get_locale_fm(lang, "not_your_button"),
                ephemeral=True,
            )
            return

        nonlocal interacted_with

        if not interacted_with:
            # add to user inventory
            filter_ = {
                "_id": ctx.author.id,
                "$expr": {"$lt": ["$inventory_size", "$inventory_max_capacity"]},
            }
            update = {
                "$push": {"inventory": item},
                "$inc": {"inventory_size": 1},
            }

            update_result = database.user_data.update_one(filter_, update)

            if update_result.modified_count == 1:
                interacted_with = True
                e.colour = discord.colour.Color.green()
                e.set_footer(text="")
                await msg.edit(embed=e, view=None)

            elif update_result.modified_count == 0:
                await msg_embed_response(
                    interact.response, get_locale_fm(lang, "inventory.full")
                )
        else:
            await interact.response.defer()

    # if not interacted with after 30 seconds, sell the item
    async def view_timeout_callback():
        nonlocal interacted_with
        if not interacted_with:
            interacted_with = True
            await sell_item()

    # create buttons
    view = discord.ui.View(timeout=30)
    view.on_timeout = view_timeout_callback
    inventory_button = discord.ui.Button(
        label=get_locale_fm(lang, "button.add_to_inventory"),
        style=discord.ButtonStyle.green,
    )
    inventory_button.callback = inventory_callback
    sell_button = discord.ui.Button(
        label=get_locale_fm(lang, "button.sell"), style=discord.ButtonStyle.red
    )
    sell_button.callback = sell_callback
    view.add_item(inventory_button)
    view.add_item(sell_button)

    # send embed
    msg = await ctx.send(embed=e, view=view)


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
