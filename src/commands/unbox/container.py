import discord
from discord.ext.commands import Context
from src.util import database
from src.util.string_util import currency_str_format, get_closest_match
from src.util.constants import conditions, rarity_color_dict

async def container(ctx:Context, *args):
    container = " ".join(args[:]).strip().lower()
    
    try:
        container_data = database.containers[container]
        container_name = container_data["formatted_name"]
        container_price = currency_str_format(container_data["price"])
        container_image_url = container_data["image_url"]
    except KeyError:
        #try and find closest match
        closest_match = get_closest_match(container, database.containers.keys())
        
        #if match is reasonably close enough
        if closest_match is None:
            await ctx.send("Container not found!")
        else:
            container_data = database.containers[closest_match]
            await ctx.send(f'Container not found! Did you mean: `{container_data["formatted_name"]}`?')
        return
        
    item_index = 0
    
    rarities = {}
    selected_rarity = "all items"
    rarities["all items"] = container_data["all items"]
    rarity_len = len(rarities[selected_rarity])

    for key, value in container_data["items"].items():
        if len(value) != 0:
            rarities[key] = value

    #create select menu and left right arrow buttons
    view = discord.ui.View(timeout=60)

    select_options = [discord.SelectOption(label="All Items", value="all items")]
    for key, rarity, in container_data["items"].items():
        if len(rarity) != 0:
            select_options.append(discord.SelectOption(label=key.title(), value=key))

    select = discord.ui.Select(options=select_options)

    async def select_callback(interact: discord.Interaction):
        nonlocal selected_rarity, item_index, rarity_len

        if interact.user.id == ctx.author.id:
            selected_rarity = select.values[0]        
            rarity_len = len(rarities[selected_rarity])
            item_index = 0
            await interact.response.edit_message(embed=get_embed(), view=view)
        else:
            await interact.response.defer()

    select.callback = select_callback

    prev_button = discord.ui.Button(label="◀", style=discord.ButtonStyle.gray)
    next_button = discord.ui.Button(label="▶", style=discord.ButtonStyle.gray)

    async def prev_callback(interact: discord.Interaction):
        nonlocal item_index

        if interact.user.id == ctx.author.id:
            if item_index == 0:
                item_index = len(rarities[selected_rarity])-1
            else:
                item_index -= 1
            await interact.response.edit_message(embed=get_embed(), view=view) 
        else:
            await interact.response.defer()

    async def next_callback(interact: discord.Interaction):
        nonlocal item_index
        
        if interact.user.id == ctx.author.id:
            if item_index == len(rarities[selected_rarity])-1:
                item_index = 0
            else:
                item_index += 1
            await interact.response.edit_message(embed=get_embed(), view=view)
        else:
            await interact.response.defer()
    
    async def on_view_timeout():
        await msg.delete()

    prev_button.callback = prev_callback
    next_button.callback = next_callback
    view.on_timeout = on_view_timeout

    view.add_item(select)
    view.add_item(prev_button)
    view.add_item(next_button)

    def get_embed():
        item = rarities[selected_rarity][item_index]
        formatted_item_name = database.skin_data[item]["formatted_name"]

        best_condition_index = database.skin_data[item]["best_condition_index"]
        worst_condition_index = database.skin_data[item]["worst_condition_index"]

        best_condition = conditions[best_condition_index].lower()
        item_data = database.skin_data[best_condition + " " + item]
        rarity = item_data["rarity"]
        rarity_color = rarity_color_dict[rarity]

        #price range string generation
        has_stattrak_variant = item_data["has_stattrak_variant"]
        has_souvenir_variant = item_data["has_souvenir_variant"]

        has_modifier_price = False

        min_price = float('inf')
        max_price = 0
        for i in range(best_condition_index, worst_condition_index+1):
            price = database.skin_data[conditions[i].lower() + " " + item]["price"]
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
            min_modifier_price = float('inf')
            max_modifier_price = 0.0
            for i in range(best_condition_index, worst_condition_index+1):
                price = database.skin_data[modifier + conditions[i].lower() + " " + item]["price"]
                if price < min_modifier_price:
                    min_modifier_price = price
                if price > max_modifier_price:
                    max_modifier_price = price

        price_range_str = f"{currency_str_format(min_price)} - {currency_str_format(max_price)}"
        if has_modifier_price: 
            price_range_str += f"\n{currency_str_format(min_modifier_price)} - {currency_str_format(max_modifier_price)}"

        #min max float
        min_float = "{:.2f}".format(item_data["min_float"])
        max_float = "{:.2f}".format(item_data["max_float"])

        image_url = item_data["image_url"]

        e = discord.Embed(title=f"{container_name} - ${container_price}\n{formatted_item_name} - ({item_index+1}/{rarity_len})", color=rarity_color)
        e.add_field(name="Price Range", value=price_range_str)
        e.add_field(name="Rarity", value=rarity)
        e.add_field(name="Float Range", value=f"{min_float} - {max_float}")
        e.set_image(url=image_url)
        e.set_thumbnail(url=container_image_url)
        return e

    msg = await ctx.send(embed=get_embed(), view=view)
        