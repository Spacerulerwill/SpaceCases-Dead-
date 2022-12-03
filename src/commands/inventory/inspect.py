import discord
from src.util import database
from src.util.constants import PREFIX
from src.util.constants import rarity_color_dict
from src.util.string_util import currency_str_format, get_inspect_link_3D
from discord.ext.commands import Context
from urllib.parse import quote

async def inspect(ctx:Context, member:discord.Member, item_index:int):

    if member is None:
        member = ctx.author

    if item_index is None:
        await ctx.send("Oops! You forgot to supply an item index")
        return

    user_data = database.user_data.find_one({"_id": member.id})

    if user_data is None:
        if member is ctx.author:
            await ctx.send(f"You are not registered! Use `{PREFIX}register` to register")
        else:
            await ctx.send(f"{member.name} is not registered!")

            
    user_inventory = list(user_data["inventory"])

    if item_index > len(user_inventory):
        await ctx.send(f"No item exists with item index {item_index}")
        return
        
    item_index -= 1

    item = user_inventory[item_index]
    
    unformatted_name = item["name"]
    float_val = str(item["float"])

    item_data = database.skin_data[unformatted_name]
    formatted_name = item_data["formatted_name"]
    price = currency_str_format(item_data["price"])

    image_url = item_data["image_url"]
    rarity = item_data["rarity"]
    rarity_color = rarity_color_dict[rarity]
    inspect_url = get_inspect_link_3D(item_data["inspect_url"])
    
    e = discord.Embed(title=formatted_name, color=rarity_color, description=f"[Inspect In 3D]({inspect_url})")
    e.add_field(name="Current Market Value", value=price)
    e.add_field(name="Float", value=float_val)
    e.add_field(name="Rarity", value=rarity)
    e.set_image(url=image_url)
    e.set_footer(icon_url=member.avatar.url, text=f"This item belongs to {member.name}")

    await ctx.send(embed=e)
