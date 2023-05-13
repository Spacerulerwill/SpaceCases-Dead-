"""
Copyright (C) 2022 William Redding - All Rights Reserved

See end of file for licence details
"""

import discord
from discord.ext.commands import Context
from src.util import database
from src.lang.lang import get_locale_fm
from src.util.item_func import get_item_embed
from src.util.string_util import currency_str_format, get_closest_match
from src.util.constants import conditions, rarity_color_dict
from src.util.embed_func import msg_embed, msg_embed_response


async def container(ctx: Context, *args):
    user_data = database.user_data.find_one({"_id": ctx.author.id})

    if user_data is None:
        lang = "en"
    else:
        lang = user_data["lang"]

    container = " ".join(args[:]).strip().lower()

    try:
        container_data = database.containers[container]
        container_name = container_data["formatted_name"]
        container_price = currency_str_format(container_data["price"])
        container_image_url = container_data["image_url"]
    except KeyError:
        # try and find closest match
        closest_match = get_closest_match(container, database.containers.keys())

        # if match is reasonably close enough
        if closest_match is None:
            await msg_embed(ctx, get_locale_fm(lang, "container.not_found"))
        else:
            container_data = database.containers[closest_match]
            await msg_embed(
                ctx,
                get_locale_fm(
                    lang,
                    "container.not_found_suggest",
                    container_data["formatted_name"],
                ),
            )
        return

    item_index = 0

    rarities = {}
    selected_rarity = "all items"
    rarities["all items"] = container_data["all items"]
    rarity_len = len(rarities[selected_rarity])

    for key, value in container_data["items"].items():
        if len(value) != 0:
            rarities[key] = value

    # create select menu and left right arrow buttons
    view = discord.ui.View(timeout=60)

    select_options = [
        discord.SelectOption(
            label=get_locale_fm(lang, "container.select.all_items"), value="all items"
        )
    ]
    for (
        key,
        rarity,
    ) in container_data["items"].items():
        if len(rarity) != 0:
            select_options.append(
                discord.SelectOption(label=get_locale_fm(lang, key), value=key)
            )

    select = discord.ui.Select(options=select_options)

    async def select_callback(interact: discord.Interaction):
        if interact.user.id != ctx.author.id:
            await msg_embed_response(
                interact.response,
                get_locale_fm(lang, "not_your_select"),
                ephemeral=True,
            )
            return

        nonlocal selected_rarity, item_index, rarity_len

        selected_rarity = select.values[0]
        rarity_len = len(rarities[selected_rarity])
        item_index = 0
        await interact.response.edit_message(embed=get_embed(), view=view)

    select.callback = select_callback

    prev_button = discord.ui.Button(label="◀", style=discord.ButtonStyle.gray)
    next_button = discord.ui.Button(label="▶", style=discord.ButtonStyle.gray)

    async def prev_callback(interact: discord.Interaction):
        if interact.user.id != ctx.author.id:
            await msg_embed_response(
                interact.response,
                get_locale_fm(lang, "not_your_button"),
                ephemeral=True,
            )
            return

        nonlocal item_index

        if item_index == 0:
            item_index = len(rarities[selected_rarity]) - 1
        else:
            item_index -= 1
        await interact.response.edit_message(embed=get_embed(), view=view)

    async def next_callback(interact: discord.Interaction):
        if interact.user.id != ctx.author.id:
            await msg_embed_response(
                interact.response,
                get_locale_fm(lang, "not_your_button"),
                ephemeral=True,
            )
            return

        nonlocal item_index

        if item_index == len(rarities[selected_rarity]) - 1:
            item_index = 0
        else:
            item_index += 1
        await interact.response.edit_message(embed=get_embed(), view=view)

    async def on_view_timeout():
        await msg.delete()

    prev_button.callback = prev_callback
    next_button.callback = next_callback
    view.on_timeout = on_view_timeout

    view.add_item(select)
    view.add_item(prev_button)
    view.add_item(next_button)

    def get_embed():
        unformatted_name = rarities[selected_rarity][item_index]

        match container_data["type"]:
            case "case" | "souvenir_package":
                # figure out price ranges for the item
                formatted_item_name = database.skin_data["no_wear_skins"][
                    unformatted_name
                ]["formatted_name"]

                best_condition_index = database.skin_data["no_wear_skins"][
                    unformatted_name
                ]["best_condition_index"]
                worst_condition_index = database.skin_data["no_wear_skins"][
                    unformatted_name
                ]["worst_condition_index"]
                best_condition = conditions[best_condition_index].lower()
                item_data = database.skin_data["skins"][
                    best_condition + " " + unformatted_name
                ]
                rarity = item_data["rarity"]
                rarity_color = rarity_color_dict[rarity]

                e = discord.Embed(
                    title=f"{container_name} - {container_price}\n{formatted_item_name} - ({item_index+1}/{rarity_len})",
                    color=rarity_color,
                )

                # price range string generation
                has_stattrak_variant = item_data["has_stattrak_variant"]
                has_souvenir_variant = item_data["has_souvenir_variant"]

                has_modifier_price = False

                min_price = float("inf")
                max_price = 0
                for i in range(best_condition_index, worst_condition_index + 1):
                    price = database.skin_data["skins"][
                        conditions[i].lower() + " " + unformatted_name
                    ]["price"]
                    if price < min_price:
                        min_price = price
                    if price > max_price:
                        max_price = price

                if has_stattrak_variant:
                    has_modifier_price = True
                    modifier = "stattrak "
                elif has_souvenir_variant:
                    has_modifier_price = True
                    modifier = "souvenir "

                if has_modifier_price:
                    min_modifier_price = float("inf")
                    max_modifier_price = 0.0
                    for i in range(best_condition_index, worst_condition_index + 1):
                        price = database.skin_data["skins"][
                            modifier + conditions[i].lower() + " " + unformatted_name
                        ]["price"]
                        if price < min_modifier_price:
                            min_modifier_price = price
                        if price > max_modifier_price:
                            max_modifier_price = price

                price_range_str = f"{currency_str_format(min_price)} - {currency_str_format(max_price)}"
                if has_modifier_price:
                    price_range_str += f"\n{currency_str_format(min_modifier_price)} - {currency_str_format(max_modifier_price)}"

                # min max float
                min_float = "{:.2f}".format(item_data["min_float"])
                max_float = "{:.2f}".format(item_data["max_float"])

                image_url = item_data["image_url"]

                e.add_field(
                    name=get_locale_fm(lang, "price_range"), value=price_range_str
                )
                e.add_field(
                    name=get_locale_fm(lang, "rarity"),
                    value=get_locale_fm(lang, rarity),
                )
                e.add_field(
                    name=get_locale_fm(lang, "float_range"),
                    value=f"{min_float} - {max_float}",
                )
                e.set_image(url=image_url)
                e.set_thumbnail(url=container_image_url)

                return e
            case "sticker_capsule":
                item_data = database.skin_data["skins"][unformatted_name]
                formatted_item_name = item_data["formatted_name"]
                image_url = item_data["image_url"]
                rarity = item_data["rarity"]
                rarity_color = rarity_color_dict[rarity]
                e = discord.Embed(
                    title=f"{container_name} - {container_price}\n{formatted_item_name} - ({item_index+1}/{rarity_len})",
                    color=rarity_color,
                )
                e.set_image(url=image_url)
                e.add_field(
                    name=get_locale_fm(lang, "rarity"),
                    value=get_locale_fm(lang, rarity),
                )
                e.add_field(
                    name=get_locale_fm(lang, "market_value"),
                    value=currency_str_format(item_data["price"]),
                )
                return e

    msg = await ctx.send(embed=get_embed(), view=view)


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
