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
            case "case" | "souvenir_package" | "package":
                # figure out price ranges for the item
                formatted_item_name = database.item_data["no_wear_skins"][
                    unformatted_name
                ]["formatted_name"]

                best_condition_index = database.item_data["no_wear_skins"][
                    unformatted_name
                ]["best_condition_index"]
                worst_condition_index = database.item_data["no_wear_skins"][
                    unformatted_name
                ]["worst_condition_index"]
                best_condition = conditions[best_condition_index].lower()
                item_data = database.item_data["items"][
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
                    price = database.item_data["items"][
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
                        price = database.item_data["items"][
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
                item_data = database.item_data["items"][unformatted_name]
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
