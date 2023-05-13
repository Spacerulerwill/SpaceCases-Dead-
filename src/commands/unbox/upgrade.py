"""
Copyright (C) 2022 William Redding - All Rights Reserved

See end of file for licence details
"""

import discord
from src.util import database
from src.lang.lang import get_locale_fm
from src.util.constants import case_wear_ranges_lower, case_wear_ranges_upper
from src.util.string_util import round_sig_fig, get_closest_match
from src.util.embed_func import msg_embed, msg_embed_response
from src.util.decorators import requires
from discord.ext.commands import Context
import random

view = discord.ui.View(timeout=30)


@requires(users_registered=True)
async def upgrade(ctx: Context, item_index: int, *args):
    result_item_name = " ".join(args[:]).strip().lower()

    user_data = database.user_data.find_one({"_id": ctx.author.id})
    lang = user_data["lang"]

    # check the item exists in their inventory
    if item_index > len(user_data["inventory"]):
        await msg_embed(ctx, get_locale_fm(lang, "inventory.not_at_index", item_index))
        return

    item_index -= 1
    start_item_name = user_data["inventory"][item_index]["name"]
    start_item_float = user_data["inventory"][item_index]["float"]

    start_item_data = database.skin_data["skins"][start_item_name]

    # check the item they want to upgrade too exists
    try:
        result_item_data = database.skin_data["skins"][result_item_name]
    except KeyError:
        # try and find closest match
        closest_match = get_closest_match(
            result_item_name, database.skin_data["skins"].keys()
        )

        # if match is reasonably close enough
        if closest_match is None:
            await msg_embed(ctx, get_locale_fm(lang, "item.not_found"))
        else:
            await msg_embed(
                ctx,
                get_locale_fm(
                    lang,
                    "item.not_found_suggest",
                    closest_match.title(),
                ),
            )
        return

    # make sure it isnt cheaper than the starting item
    if result_item_data["price"] <= start_item_data["price"]:
        await msg_embed(ctx, get_locale_fm(lang, "upgrade.cant_upgrade_to_cheaper"))
        return

    # price multiplier
    price_multiplier = result_item_data["price"] / start_item_data["price"]
    percentage_chance = 1 / price_multiplier
    has_upgraded = False

    # create embed
    e = discord.Embed(
        description=get_locale_fm(
            lang,
            "upgrade.embed.title",
            start_item_data["formatted_name"],
            result_item_data["formatted_name"],
        )
    )
    e.add_field(
        name=get_locale_fm(lang, "price_multiplier"),
        value=f"{round_sig_fig(price_multiplier, 2)}X",
    )
    e.add_field(
        name=get_locale_fm(lang, "chance"),
        value=f"{round_sig_fig(percentage_chance*100, 2)}%",
    )
    e.set_thumbnail(url=start_item_data["image_url"])
    e.set_image(url=result_item_data["image_url"])
    e.set_footer(
        icon_url=ctx.author.display_avatar.url,
        text=get_locale_fm(lang, "upgrade.embed.footer"),
    )

    # callback functions
    async def on_view_timeout():
        if not has_upgraded:
            await msg.delete()

    async def upgrade_callback(interact: discord.Interaction):
        nonlocal has_upgraded, e

        if interact.user.id != ctx.author.id:
            await msg_embed_response(
                interact.response,
                get_locale_fm(lang, "not_your_button"),
                ephemeral=True,
            )
            return

        if random.random() < percentage_chance:
            # upgrade successful - replace item
            # start a session to multi document atomic transaction
            with database.mongo_client.start_session() as session:
                with session.start_transaction():
                    update_result = database.user_data.update_one(
                        {"_id": ctx.author.id},
                        {
                            "$pull": {
                                "inventory": {
                                    "name": start_item_name,
                                    "float": start_item_float,
                                }
                            },
                            "$inc": {"inventory_size": -1},
                        },
                        session=session,
                    )

                    # failed to pull - item no longer exists abort transaction
                    if update_result.modified_count == 0:
                        e = discord.Embed(
                            title=get_locale_fm(lang, "upgrade.error.title"),
                            description=get_locale_fm(
                                lang,
                                "upgrade.error.item_missing",
                                start_item_data["formatted_name"],
                            ),
                        )
                        e.set_thumbnail(url=ctx.author.display_avatar.url)
                        session.abort_transaction()
                    else:
                        # successful at pull, push new item with a new random float
                        worst_condition_float = case_wear_ranges_upper[
                            result_item_data["condition_index"]
                        ]

                        if result_item_data["max_float"] < worst_condition_float:
                            worst_condition_float = result_item_data["max_float"]

                        best_condition_float = case_wear_ranges_lower[
                            result_item_data["condition_index"]
                        ]

                        if result_item_data["min_float"] > best_condition_float:
                            best_condition_float = result_item_data["min_float"]

                        upgraded_item_float = random.uniform(
                            worst_condition_float, best_condition_float
                        )

                        database.user_data.update_one(
                            {"_id": ctx.author.id},
                            {
                                "$push": {
                                    "inventory": {
                                        "name": result_item_name,
                                        "float": upgraded_item_float,
                                    }
                                },
                                "$inc": {"inventory_size": 1},
                            },
                            session=session,
                        )
                        e.color = discord.Color.green()
                        e.set_footer(text=None)
        else:
            # upgrade not successful - remove item
            # start a session to multi docuemnt atomic transaction
            with database.mongo_client.start_session() as session:
                with session.start_transaction():
                    update_result = database.user_data.update_one(
                        {"_id": ctx.author.id},
                        {
                            "$pull": {
                                "inventory": {
                                    "name": start_item_name,
                                    "float": start_item_float,
                                }
                            },
                        },
                        session=session,
                    )

                    # failed to pull - item no longer exists abort transaction
                    if update_result.modified_count == 0:
                        e = discord.Embed(
                            title=get_locale_fm(lang, "upgrade.error.title"),
                            description=get_locale_fm(
                                lang,
                                "upgrade.error.item_missing",
                                result_item_data["formatted_name"],
                            ),
                        )
                        e.set_thumbnail(url=ctx.author.display_avatar.url)
                        session.abort_transaction()
                    else:
                        # successful at pull, decrement inventory size
                        database.user_data.update_one(
                            {"_id": ctx.author.id},
                            {"$inc": {"inventory_size": -1}},
                            session=session,
                        )
                        e.color = discord.Color.red()
                        e.set_footer(text=None)

        has_upgraded = True
        await msg.edit(embed=e, view=None)

    view.on_timeout = on_view_timeout

    upgrade_button = discord.ui.Button(
        label=get_locale_fm(lang, "button.upgrade"), style=discord.ButtonStyle.green
    )
    upgrade_button.callback = upgrade_callback
    view.add_item(upgrade_button)

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
