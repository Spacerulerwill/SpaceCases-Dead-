import discord
from discord.ext.commands import Context
from src.util.constants import PREFIX, INVENTORY_ELEMS_PER_PAGE, rarity_emoji_dict
from src.util.decorators import requires
from src.util.embed_func import msg_embed
from src.util import database
from src.util.string_util import currency_str_format

@requires(users_registered=True)
async def inventory(ctx:Context, member:discord.Member, page:int):

    if member == None:
        member = ctx.author
    
    user_data = database.user_data.find_one({"_id": member.id})

    # if users inventory is empty
    if len(user_data["inventory"]) == 0:
        e = discord.Embed(title=f"{member.name}'s Inventory", color=discord.Color.dark_theme())
        e.set_thumbnail(url=member.display_avatar.url)

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
        await msg_embed(ctx, "Invalid inventory page!")
        return
    
    page -= 1
    inventory_value = sum([database.skin_data[item["name"]]["price"] for item in inventory_data])

    # get inventory embed by function
    async def get_inventory_embed() -> discord.Embed:
        inventory_page = inventory_pages[page]

        string = ""
        for count, item in enumerate(inventory_page):
            skin_data = database.skin_data[item["name"]]
            emoji = rarity_emoji_dict[skin_data["rarity"]]
            string += f"{emoji} **{count+ (page*INVENTORY_ELEMS_PER_PAGE) + 1})** `{skin_data['formatted_name']}` - **{currency_str_format(skin_data['price'])}**\n"

        e = discord.Embed(title=f"{member.name}'s Inventory - {page+1}/{len(inventory_pages)}", color=discord.Color.dark_theme())
        e.set_thumbnail(url=member.display_avatar.url)
        
        e.description = f"Total value: **{currency_str_format(inventory_value)}**\nSlots Used: **{user_data['inventory-size']}/{user_data['inventory-max-capacity']}**"
        e.add_field(name="Contents", value=string)

        if member is ctx.author:
            e.add_field(name="Commands", value=f"`{PREFIX}inspect <item number>` - view an item\n`{PREFIX}sell <item number>` - sell an item", inline=False)
        else:
            e.add_field(name="Commands", value=f"`{PREFIX}inspect {member.name} <item number>` - see an item", inline=False)

        return e

    # view and button callbacks
    async def prev_callback(interact:discord.Interaction):
        nonlocal page

        if page == 0:
            page = len(inventory_pages) - 1
        else:
            page -= 1

        await interact.response.edit_message(embed=await get_inventory_embed(), view=view)

    async def next_callback(interact:discord.Interaction):
        nonlocal page

        if page == len(inventory_pages) - 1:
            page = 0
        else:
            page += 1

        await interact.response.edit_message(embed=await get_inventory_embed(), view=view)

    view = None

    #only need buttons if inventory pages greater than 1
    if len(inventory_pages) > 1:
        view = discord.ui.View()
        prev_button = discord.ui.Button(label="◀", style=discord.ButtonStyle.gray)
        prev_button.callback = prev_callback
        next_button = discord.ui.Button(label="▶", style=discord.ButtonStyle.gray)
        next_button.callback = next_callback
        view.add_item(prev_button)
        view.add_item(next_button)
    
    await ctx.send(embed=await get_inventory_embed(), view=view)