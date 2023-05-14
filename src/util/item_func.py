"""
Copyright (C) 2023 William Redding - All Rights Reserved

Item related functionality

Functions
~~~~~~~~~
* gen_item
* get_item_embed

See end of file for licence details
"""

import discord
from src.util import database
from src.util.constants import case_wear_ranges_lower, conditions, rarity_color_dict
from src.util.string_util import currency_str_format
from src.lang.lang import get_locale_fm
import random


def gen_item(unformatted_name: str, container_type: str) -> dict:
    """Randomly generate a float and condition for a skin given its name, and determine if it's statrak or souvenir

    Args:
        unformatted_name: the unformatted name of the skin
    Returns:
        the new item in form of a dict
    """
    match container_type:
        case "case" | "souvenir_package" | "package":
            skin_data = database.item_data["no_wear_skins"][unformatted_name]

            # select skin float
            min_float = skin_data["min_float"]
            max_float = skin_data["max_float"]

            float_value = random.random()

            # determine condition
            if float_value > 0 and float_value <= 0.1471:
                float_value = random.uniform(0.00, 0.07)
            elif float_value > 0.1471 and float_value <= 0.3939:
                float_value = random.uniform(0.07, 0.15)
            elif float_value > 0.3939 and float_value <= 0.8257:
                float_value = random.uniform(0.15, 0.38)
            elif float_value > 0.8257 and float_value <= 0.9007:
                float_value = random.uniform(0.38, 0.45)
            elif float_value > 0.9007 and float_value <= 1.0:
                float_value = random.uniform(0.45, 1)

            # linear interpolate between max and min float
            final_float = float_value * (max_float - min_float) + min_float

            for wear, upper in case_wear_ranges_lower.items():
                if final_float > upper:
                    condition = conditions[wear].lower() + " "
                    break

            # modifier
            modifier = ""
            if skin_data["has_souvenir_variant"]:
                if container_type == "souvenir_package":
                    modifier = "souvenir "
            elif skin_data["has_stattrak_variant"]:
                if container_type in ["case", "package"]:
                    if random.random() < 0.1:
                        modifier = "stattrak "

            unformatted_name = modifier + condition + unformatted_name

            return {"name": unformatted_name, "float": final_float}
        case "sticker_capsule":
            return {"name": unformatted_name}


def get_item_embed(lang: str, item_data: dict) -> discord.Embed:
    match item_data["item_type"]:
        case "weapon":
            # gather all the information from the item data
            formatted_name = item_data["formatted_name"]
            price = currency_str_format(item_data["price"])

            image_url = item_data["image_url"]
            rarity = item_data["rarity"]
            rarity_color = rarity_color_dict[rarity]
            min_float = "{:.2f}".format(item_data["min_float"])
            max_float = "{:.2f}".format(item_data["max_float"])

            # create an embed and add all the data
            e = discord.Embed(
                title=formatted_name,
                color=rarity_color,
            )
            e.add_field(name=get_locale_fm(lang, "market_value"), value=price)
            e.add_field(
                name=get_locale_fm(lang, "rarity"), value=get_locale_fm(lang, rarity)
            )
            e.add_field(
                name=get_locale_fm(lang, "float_range"),
                value=f"{min_float} - {max_float}",
            )
            e.set_image(url=image_url)

        case "sticker":
            # gather all the information from the item data
            formatted_name = item_data["formatted_name"]
            price = currency_str_format(item_data["price"])

            image_url = item_data["image_url"]
            rarity = item_data["rarity"]
            rarity_color = rarity_color_dict[rarity]

            # create an embed and add all the data
            e = discord.Embed(
                title=formatted_name,
                color=rarity_color,
            )
            e.add_field(name=get_locale_fm(lang, "market_value"), value=price)
            e.add_field(
                name=get_locale_fm(lang, "rarity"), value=get_locale_fm(lang, rarity)
            )
            e.set_image(url=image_url)

    return e

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