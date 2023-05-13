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
from src.util.string_util import currency_str_format, get_inspect_link_3D
from src.lang.lang import get_locale_fm
import random


def gen_item(unformatted_name: str, container_type: str) -> dict:
    """Randomly generate a float and condition for a skin given its name, and determine if it's statrak

    Args:
        unformatted_name: the unformatted name of the skin
    Returns:
        a tuple of the new skin name and its float value
    """
    match container_type:
        case "case" | "souvenir_package":
            skin_data = database.skin_data["no_wear_skins"][unformatted_name]

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
                if container_type == "case":
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
            inspect_url = get_inspect_link_3D(item_data["inspect_url"])

            # create an embed and add all the data
            e = discord.Embed(
                title=formatted_name,
                color=rarity_color,
                description=get_locale_fm(lang, "inspect_in_3d", inspect_url),
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
