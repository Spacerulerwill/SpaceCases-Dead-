import discord
from discord.ext.commands import Context
from src.util import database
from src.lang.lang import get_locale_fm
from src.util.string_util import (
    currency_str_format,
    get_inspect_link_3D,
    get_closest_match,
)
from src.util.constants import rarity_color_dict
from src.util.embed_func import msg_embed


async def item(ctx: Context, *args):
    user_data = database.user_data.find_one({"_id": ctx.author.id})

    # if they have no user data - default language is english
    if user_data is None:
        lang = "en"
    else:
        lang = user_data["lang"]

    item_query = " ".join(args[:]).strip().lower()

    try:
        skin_data = database.skin_data["skins"][item_query]
    except KeyError:
        # try and find closest match
        closest_match = get_closest_match(
            item_query, database.skin_data["skins"].keys()
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

    # gather all the information from the item data
    formatted_name = skin_data["formatted_name"]
    price = currency_str_format(skin_data["price"])

    image_url = skin_data["image_url"]
    rarity = skin_data["rarity"]
    rarity_color = rarity_color_dict[rarity]
    min_float = "{:.2f}".format(skin_data["min_float"])
    max_float = "{:.2f}".format(skin_data["max_float"])
    inspect_url = get_inspect_link_3D(skin_data["inspect_url"])

    # create an embed and add all the data
    e = discord.Embed(
        title=formatted_name,
        color=rarity_color,
        description=get_locale_fm(lang, "inspect_in_3d", inspect_url),
    )
    e.add_field(name=get_locale_fm(lang, "market_value"), value=price)
    e.add_field(name=get_locale_fm(lang, "rarity"), value=get_locale_fm(lang, rarity))
    e.add_field(
        name=get_locale_fm(lang, "float_range"), value=f"{min_float} - {max_float}"
    )
    e.set_image(url=image_url)

    await ctx.send(embed=e)
