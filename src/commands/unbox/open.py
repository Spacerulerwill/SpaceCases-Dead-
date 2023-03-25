import discord
import random
from discord.ext.commands import Context
from src.util import database
from src.util.lang import get_locale
from src.util.decorators import requires
from src.util.constants import KEY_PRICE, case_rarity_odds, rarity_color_dict
from src.util.string_util import currency_str_format, get_closest_match, get_inspect_link_3D
from src.util.skin_func import gen_item
from src.util.embed_func import msg_embed, msg_embed_response

@requires(room=True, users_registered=True)
async def open(ctx:Context, *args):
    container_name = " ".join(args[:]).strip().lower()

    user_data = database.user_data.find_one({"_id": ctx.author.id})
    lang = user_data["language"]
    
    # check case exists
    try:
        container_data = database.containers[container_name]
        container_price = container_data["price"]
    except KeyError:
        # try and find closest match
        closest_match = get_closest_match(container_name, database.containers.keys())
        
        #if match is reasonably close enough
        if closest_match is None:
            await msg_embed(ctx, get_locale(lang, "container.not_found"))
        else:
            container_data = database.containers[closest_match]
            await msg_embed(ctx, get_locale(lang, "container.not_found_suggest",{container_data["formatted_name"]}))
    
    # check user has enough balance for case
    if user_data["balance"] < container_data["price"] + KEY_PRICE:
        await msg_embed(ctx, get_locale(lang, "not_enough_funds"))
        return

    # select skin rarity
    rarity_rand = random.random()
    for key, value in case_rarity_odds.items():
        if rarity_rand > value:
            rarity = key
            break
    
    skin_pool = container_data["items"][rarity]
    unformatted_name, float_val = gen_item(random.choice(skin_pool))
    
    skin_data = database.skin_data["skins"][unformatted_name]

    formatted_name = skin_data["formatted_name"]
    image_url = skin_data["image_url"]
    skin_rarity = skin_data["rarity"]
    color = rarity_color_dict[skin_rarity]
    skin_price = skin_data["price"]
    inspect_url = get_inspect_link_3D(skin_data["inspect_url"])

    #decrement balance, increment total spent, increase total return and containers opened
    database.user_data.update_one({"_id": ctx.author.id},{"$inc" :{
        "balance" : -(container_price + KEY_PRICE), 
        "stats.total-spent": container_price + KEY_PRICE, 
        "stats.total-return": skin_price, 
        "stats.containers-opened": 1
    }})

    # create embed to show user
    e = discord.Embed(title=formatted_name, color=color, description=get_locale(lang, "inspect_in_3d", inspect_url))
    e.add_field(name=get_locale(lang, "market_value"), value=currency_str_format(skin_price))
    e.add_field(name=get_locale(lang, "rarity"), value=get_locale(lang, skin_rarity))
    e.add_field(name=get_locale(lang, "float"), value=str(float_val)) 
    e.set_image(url=image_url)
    e.set_footer(text=get_locale(lang, "open.embed.footer"))

    interacted_with = False

    # callbacks
    async def sell_item():
        #change color to dark gray, remove footer, change balance to have balance of skin
        database.user_data.update_one({"_id": ctx.author.id}, {"$inc" :{"balance" : skin_price}})

        e.colour = discord.colour.Color.dark_gray()
        e.set_footer(text="")

        await msg.edit(embed=e, view=None)
    
    async def sell_callback(interact:discord.Interaction):
        if ctx.author.id != interact.user.id:
            await msg_embed_response(interact.response, get_locale(lang, "not_your_button"), ephemeral=True)
            return

        nonlocal interacted_with

        if not interacted_with:
            interacted_with = True
            await sell_item()
        else:
            await interact.response.defer()
    
    async def inventory_callback(interact:discord.Interaction):
        if ctx.author.id != interact.user.id:
            await msg_embed_response(interact.response, get_locale(lang, "not_your_button"), ephemeral=True)
            return

        nonlocal interacted_with
        
        if not interacted_with:
              
            # add to user inventory
            filter_ = {
                '_id': ctx.author.id,
                "$expr":{ "$lt" : ["$inventory-size", "$inventory-max-capacity"]}
            }
            update =  {
                '$push': { 
                    'inventory':  {"name": unformatted_name, "float": float_val}
                },
                "$inc": {
                    "inventory-size": 1
                }
            }

            update_result = database.user_data.update_one(filter_, update)    
                    
            if update_result.modified_count == 1:
                interacted_with = True
                e.colour = discord.colour.Color.green()
                e.set_footer(text="")
                await  msg.edit(embed=e, view=None)
                
            elif update_result.modified_count == 0:
                await msg_embed_response(interact.response, get_locale(lang, "inventory.full"))
        else:
            await interact.response.defer()

    #if not interacted with after 30 seconds, sell the item
    async def view_timeout_callback():
        nonlocal interacted_with
        if not interacted_with:
            interacted_with = True
            await sell_item()

    #create buttons
    view = discord.ui.View(timeout=30)
    view.on_timeout= view_timeout_callback
    inventory_button = discord.ui.Button(label=get_locale(lang, "button.add_to_inventory"), style=discord.ButtonStyle.green)
    inventory_button.callback=inventory_callback
    sell_button = discord.ui.Button(label=get_locale(lang, "button.sell"), style=discord.ButtonStyle.red)
    sell_button.callback=sell_callback
    view.add_item(inventory_button)
    view.add_item(sell_button)

    # send embed
    msg = await ctx.send(embed=e, view=view)