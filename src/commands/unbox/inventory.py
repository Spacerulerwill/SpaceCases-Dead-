import discord
from discord.ext.commands import Context
from src.util.constants import PREFIX, INVENTORY_ELEMS_PER_PAGE
from src.util import database
from src.util.format import currency_str_format

async def inventory(ctx:Context, member:discord.Member, page:int):

    if member == None:
        member = ctx.author
    
    user_data = database.user_data.find_one({"_id":member.id})

    # if user doesn't exist
    if user_data == None:
        if member == ctx.author:
            await ctx.send(f"You are not registered! Use `{PREFIX}register` to register")
        else:
            await ctx.send(f"{member.name} is not registered!")
        return
    

    # if users inventory is empty
    if len(user_data["inventory"]) == 0:
        e = discord.Embed(title=f"{member.name}'s Inventory", color=discord.Color.blue())

        if member == ctx.author:
            e.description = f"Your inventory is empty! Start unboxing with `{PREFIX}open`"
        else:
            e.description = f"{member.name}'s inventory is empty!"
        await ctx.send(embed=e)
        return

    # split into even chunks for pages
    inventory_data = list(user_data["inventory"])
    inventory_pages = [inventory_data[x:x+INVENTORY_ELEMS_PER_PAGE] for x in range(0, len(inventory_data), INVENTORY_ELEMS_PER_PAGE)]

    if page <= 0 or page > len(inventory_pages):
        await ctx.send("Invalid inventory page!")
        return
    
    page -= 1
    inventory_value = sum([database.skin_data[item["name"]]["price"] for item in inventory_data])
    inventory_page = inventory_pages[page]

    string = ""
    for count, item in enumerate(inventory_page):
        skin_data = database.skin_data[item["name"]]
        string += f"**{count+1})** {skin_data['formatted_name']} - **{currency_str_format(skin_data['price'])}**\n"

    e = discord.Embed(title=f"{member.name}'s Inventory - {page+1}/{len(inventory_pages)}", color=discord.Color.blue())
    
    e.description = f"Total value: **{currency_str_format(inventory_value)}**\nSlots Used: **{len(inventory_data)}/{user_data['inventory-size']}**"
    e.add_field(name="Contents", value=string)
    e.set_thumbnail(url=ctx.author.avatar.url)
    e.add_field(name="Commands", value=f"`{PREFIX}inspect <item number>` - view an item\n`{PREFIX}sell <item number>` - sell an item", inline=False)
    await ctx.send(embed=e)