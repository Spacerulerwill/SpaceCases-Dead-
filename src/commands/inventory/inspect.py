import discord
from src.util import database
from src.lang.lang import get_locale_fm
from src.util.constants import rarity_color_dict
from src.util.decorators import requires
from src.util.string_util import currency_str_format, get_inspect_link_3D
from src.util.embed_func import msg_embed
from discord.ext.commands import Context


@requires(users_registered=True)
async def inspect(ctx: Context, member: discord.Member, item_index: int):
    if member is None:
        member = ctx.author

    user_data = database.user_data.find_one({"_id": member.id})
    lang = user_data["lang"]
    user_inventory = list(user_data["inventory"])

    if item_index > len(user_inventory):
        await msg_embed(
            ctx, get_locale_fm(lang, "inventory.not_found_index", item_index)
        )
        return

    item_index -= 1

    item = user_inventory[item_index]

    unformatted_name = item["name"]
    float_val = str(item["float"])

    item_data = database.skin_data["skins"][unformatted_name]
    formatted_name = item_data["formatted_name"]
    price = currency_str_format(item_data["price"])

    image_url = item_data["image_url"]
    rarity = item_data["rarity"]
    rarity_color = rarity_color_dict[rarity]
    inspect_url = get_inspect_link_3D(item_data["inspect_url"])

    e = discord.Embed(
        title=formatted_name,
        color=rarity_color,
        description=get_locale_fm(lang, "inspect_in_3d", inspect_url),
    )
    e.add_field(name=get_locale_fm(lang, "market_value"), value=price)
    e.add_field(name=get_locale_fm(lang, "float"), value=float_val)
    e.add_field(name=get_locale_fm(lang, "rarity"), value=get_locale_fm(lang, rarity))
    e.set_image(url=image_url)
    e.set_footer(
        icon_url=member.display_avatar.url, text=f"This item belongs to {member.name}"
    )

    await ctx.send(embed=e)
