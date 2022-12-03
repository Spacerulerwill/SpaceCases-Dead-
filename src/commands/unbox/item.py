import discord
from discord.ext.commands import Context
from src.util import database
from src.util.string_util import currency_str_format
from src.util.constants import rarity_color_dict
from urllib.parse import quote

async def item(ctx:Context, *args):
    item_query = " ".join(args[:]).strip().lower()

    if item_query not in database.skin_data:
        await ctx.send("Could not find weapon")
        return
    try:
        weapon_data = database.skin_data[item_query]

        formatted_name = weapon_data["formatted_name"]
        price = currency_str_format(weapon_data["price"])

        image_url = weapon_data["image_url"]
        rarity = weapon_data["rarity"]
        rarity_color = rarity_color_dict[rarity]
        min_float = "{:.2f}".format(weapon_data["min_float"])
        max_float = "{:.2f}".format(weapon_data["max_float"])
        inspect_url = "https://skinbaron.de/en/3dviewer?inspectLink=" + quote(weapon_data["inspect_url"])
        
        e = discord.Embed(title=formatted_name, color=rarity_color, description=f"[Inspect In 3D]({inspect_url})")
        e.add_field(name="Current Market Value", value=price)
        e.add_field(name="Rarity", value=rarity)
        e.add_field(name="Float Range", value=f"{min_float} - {max_float}")
        e.set_image(url=image_url)

        await ctx.send(embed=e)
    except KeyError:
        await ctx.send("Could not find weapon")
        return