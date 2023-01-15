import discord
from discord.ext.commands import Context
from src.util import database
from src.util.string_util import currency_str_format, get_inspect_link_3D, get_closest_match
from src.util.constants import rarity_color_dict
from src.util.embed_func import msg_embed
from timeit import default_timer as timer
from datetime import timedelta

async def item(ctx:Context, *args):
    item_query = " ".join(args[:]).strip().lower()

    if item_query not in database.skin_data:
        await msg_embed(ctx, "Could not find item!")
        return
        
    try:
        skin_data = database.skin_data[item_query]

        formatted_name = skin_data["formatted_name"]
        price = currency_str_format(skin_data["price"])

        image_url = skin_data["image_url"]
        rarity = skin_data["rarity"]
        rarity_color = rarity_color_dict[rarity]
        min_float = "{:.2f}".format(skin_data["min_float"])
        max_float = "{:.2f}".format(skin_data["max_float"])
        inspect_url = get_inspect_link_3D(skin_data["inspect_url"])
        
        e = discord.Embed(title=formatted_name, color=rarity_color, description=f"[Inspect In 3D]({inspect_url})")
        e.add_field(name="Current Market Value", value=price)
        e.add_field(name="Rarity", value=rarity)
        e.add_field(name="Float Range", value=f"{min_float} - {max_float}")
        e.set_image(url=image_url)

        await ctx.send(embed=e)
    except KeyError:
        await msg_embed(ctx, "Could not find weapon")
        return