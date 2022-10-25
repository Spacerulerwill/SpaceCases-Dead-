# This cog is for skin unboxing related commands
# Commands:
# * open
# * item
# * container
# * containers
# * upgrade

import discord
from discord.ext import commands
from src.util.constants import PREFIX, KEY_PRICE
from src.util.format import remove_skin_name_formatting
from src.util.constants import conditions, rarity_color_dict, case_rarity_odds, case_wear_ranges
from src.util import database
import random
from decimal import Decimal
import asyncio

containerlist_pages = {
    "Cases": 
        ["""Operation Riptide Case
        Snakebite Case
        Broken Fang Case
        Fracture Case
        Prisma 2 Case
        Shattered Web Case
        CS20 Case
        Prisma Case
        Danger Zone Case
        Horizon Case
        Clutch Case
        Spectrum 2 Case""",

        """Operation Hydra Case
        Spectrum Case
        Glove Case
        Gamma 2 Case
        Gamma Case
        Chroma 3 Case
        Operation Wildfire Case
        Revolver Case
        Shadow Case
        Falcion Case
        Chroma 2 Case
        Chroma Case""",
        """
        Operation Vanguard Weapon Case
        eSports 2014 Summer Case
        Operation Breakout Weapon Case
        Huntsman Weapon Case
        Operation Phoenix Weapon Case
        CSGO Weapon Case 3
        Winter Offensive Weapon Case
        eSports 2013 Winter Case
        CSGO Weapon Case 2
        Operation Bravo Case
        eSports 2013 Case
        CSGO Weapon Case
        """]
}

len_containerlist_pages = len(containerlist_pages)

# initialise class
class Unboxing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # inspect a skins image and information
    @commands.command(description="View details for an item", usage=f"""
    `{PREFIX}item <item name>`
    **Arguments**
    `<item name>` - item name as a string
    **Additional Information**
    Different items have different naming conventions, such as:
    `Weapons - <modifier> <condition> <weapon name> <skin name>`
    """)
    async def item(self, ctx, *args):
        item_query = " ".join(args[:]).strip().lower()

        if item_query not in database.skin_data:
            await ctx.send("Could not find weapon")
            return
        try:
            weapon_data = database.skin_data[item_query]

            formatted_name = weapon_data["formatted_name"]
            price = "$" + str((Decimal(weapon_data["price"]) / 100).quantize(Decimal('0.01')))

            image_url = weapon_data["image_url"]
            rarity = weapon_data["rarity"]
            rarity_color = rarity_color_dict[rarity]
            min_float = "{:.2f}".format(weapon_data["min_float"])
            max_float = "{:.2f}".format(weapon_data["max_float"])
            e = discord.Embed(title=formatted_name, color=rarity_color)
            e.add_field(name="Current Market Value", value=price)
            e.add_field(name="Rarity", value=rarity)
            e.add_field(name="Float Range", value=f"{min_float} - {max_float}")
            e.set_image(url=image_url)

            await ctx.send(embed=e)
        except KeyError:
            await ctx.send("Could not find weapon")
            return

    # view a containers price and contents
    @commands.command(description="View a container's price and contents", usage=f"""
    `{PREFIX}container <container name>`
    **Arguments**
    `<container name>` - container name as a string
    """)
    async def container(self, ctx, *args):
        container = " ".join(args[:]).strip().lower()

        if container not in database.containers:
            await ctx.send("Invalid container!")
            return
        
        item_index = 0

        container_data = database.containers[container]
        container_name = container_data["formatted_name"]
        container_price = str((Decimal(container_data["price"]) / 100).quantize(Decimal('0.01')))
        container_image_url = container_data["image_url"]
        
        rarities = {}
        selected_rarity = "all items"
        rarities["all items"] = container_data["all items"]
        rarity_len = len(rarities[selected_rarity])

        for key, value in container_data["items"].items():
            if len(value) != 0:
                rarities[key] = value

        #create select menu and left right arrow buttons
        view = discord.ui.View()

        select_options = [discord.SelectOption(label="All Items", value="all items")]
        for key, rarity, in container_data["items"].items():
            if len(rarity) != 0:
                select_options.append(discord.SelectOption(label=key.title(), value=key))

        select = discord.ui.Select(options=select_options)

        async def select_callback(interact):
            nonlocal selected_rarity, item_index, rarity_len

            if interact.user.id == ctx.author.id:
                selected_rarity = select.values[0]        
                rarity_len = len(rarities[selected_rarity])
                item_index = 0
                await msg.edit(embed=get_embed(), view=view)

            await interact.response.defer()

        select.callback = select_callback

        prev_button = discord.ui.Button(label="◀", style=discord.ButtonStyle.gray)
        next_button = discord.ui.Button(label="▶", style=discord.ButtonStyle.gray)

        async def prev_callback(interact):
            nonlocal item_index

            if interact.user.id == ctx.author.id:
                if item_index == 0:
                    item_index = len(rarities[selected_rarity])-1
                else:
                    item_index -= 1
                await msg.edit(embed=get_embed(), view=view)

            await interact.response.defer()

        async def next_callback(interact):
            nonlocal item_index
            
            if interact.user.id == ctx.author.id:
                if item_index == len(rarities[selected_rarity])-1:
                    item_index = 0
                else:
                    item_index += 1
                await msg.edit(embed=get_embed(), view=view)

            await interact.response.defer()

        next_button.callback = next_callback
        prev_button.callback = prev_callback

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
                price = (Decimal(database.skin_data[conditions[i].lower() + " " + item]["price"] )/100).quantize(Decimal('0.01'))
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
                    price = (Decimal(database.skin_data[modifier + conditions[i].lower() + " " + item]["price"])/100).quantize(Decimal('0.01'))
                    if price < min_modifier_price:
                        min_modifier_price = price
                    if price > max_modifier_price:
                        max_modifier_price = price

            price_range_str = f"${min_price} - ${max_price}"
            if has_modifier_price: 
                price_range_str += f"\n${min_modifier_price} - ${max_modifier_price}"

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

    # see a list of all containers
    @commands.command(description="See a list of all purchasable containers", usage=f"""
    `{PREFIX}containers`
    """)
    async def containers(self, ctx, page:int = 1):
        if page <= 0 or page > len_containerlist_pages:
            await ctx.send("Invalid page number!")
            return

        page -= 1
        page_title, page_fields = list(containerlist_pages.items())[page]
        e = discord.Embed(title=f"Page {page+1}/{len_containerlist_pages}", description=f"Use `{PREFIX}container <container>` to see a container's contents and `{PREFIX}open <container>` to open one")

        for field in page_fields:
            e.add_field(name=page_title, value=field)

        await ctx.send(embed=e)

    @containers.error
    async def containerlist_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Page number must be an integer!")

    # open a container
    @commands.command(description="Purchase and open a container, with the option to either sell it or add it to your inventory", usage=f"""
    `{PREFIX}open <container name>`
    **Arguments**
    `<container name>` - the name of the container to open as a string
    """)
    async def open(self, ctx, *args):
        container_name = " ".join(args[:]).strip().lower()
        
        if container_name not in database.containers:
            await ctx.send("Container does not exist!")
            return

        user = database.user_data.find_one({"_id": ctx.author.id})

        if user == None:
            await ctx.send(f"You aren't registed! Use `{PREFIX}register` to register")
            return

        container = database.containers[container_name]

        container_price = container["price"]

        user_balance = user["balance"]

        #if they don't have enough
        if user_balance < container_price + KEY_PRICE:
            await ctx.send("Not enough balance to perform this action")
            return

        # get rarity
        rarity_rand = random.random()
        skin_rarity = None

        for rarity, upper in case_rarity_odds.items():
            if rarity_rand > upper:
                skin_rarity = rarity
                break
        
        # get skin
        skins_list = container["items"][skin_rarity]
        skin_name = random.choice(skins_list)

        # float and condition
        min_float = database.skin_data[skin_name]["min_float"]
        max_float = database.skin_data[skin_name]["max_float"]

        float_value = random.random()
        
        #determine condition
        if float_value > 0 and float_value <= 0.1471:
            float_value = random.uniform(0.00, 0.07)
        elif float_value > 0.1471 and float_value <=  0.3939:
            float_value = random.uniform(0.07, 0.15)
        elif float_value > 0.3939 and float_value <= 0.8257:
            float_value = random.uniform(0.15, 0.38)
        elif float_value > 0.8257 and float_value <=   0.9007:
            float_value = random.uniform(0.38, 0.45)
        elif float_value > 0.9007 and float_value <= 1.0:
            float_value = random.uniform(0.45, 1)

        #linear interpolate between max and min float
        final_float = float_value * (max_float - min_float) + min_float

        skin_wear = None
        for wear, upper in case_wear_ranges.items():
            if final_float > upper:
                skin_wear = conditions[wear]
                break

        final_float = str(final_float)

        #if is stattrak?
        if random.random() < 0.1:
            stattrak = "StatTrak "
        else:
            stattrak = ""

        # create embed and show player
        formatted_name = stattrak + skin_wear + " " + database.skin_data[skin_name]["formatted_name"] 

        skin_name = stattrak.lower() + remove_skin_name_formatting(skin_wear) + " " + skin_name
        
        image_url = database.skin_data[skin_name]["image_url"]
        skin_rarity = database.skin_data[skin_name]["rarity"]
        color = rarity_color_dict[skin_rarity]
        
        skin_price = database.skin_data[skin_name]["price"]
        
        #decrement balance, increment total spent, increase total return and containers opened
        database.user_data.find_one_and_update({"_id": ctx.author.id},{"$inc" :{
            "balance" : -(container_price + KEY_PRICE), 
            "total-spent": container_price + KEY_PRICE, 
            "total-return": skin_price, 
            "containers-opened": 1
        }})

        e = discord.Embed(title=formatted_name, color=color)
        e.add_field(name="Market Value", value="$" + str((Decimal(skin_price) / 100).quantize(Decimal('0.01'))))
        e.add_field(name="Rarity", value=skin_rarity)
        e.add_field(name="Float", value=final_float) 
        e.set_image(url=image_url)
        e.set_footer(text="Warning! Items are automatically sold after 30 seconds")

        #create buttons
        view = discord.ui.View(timeout=30)
        sell = discord.ui.Button(style=discord.ButtonStyle.red, label="Sell")
        inventory = discord.ui.Button(style=discord.ButtonStyle.green, label="Add to Inventory")
        view.add_item(item=sell)
        view.add_item(item=inventory)

        is_sold = False

        #call back for adding to inventory
        async def inventory_callback(interact):
            nonlocal user

            if ctx.author.id == interact.user.id:
                user = database.user_data.find_one({"_id": ctx.author.id})
                
                # add to inventory if there is room
                inventory = list(user["inventory"])

                if len(inventory) < user["inventory-size"]:

                    # add to user inventory
                    database.user_data.find_one_and_update({"_id": ctx.author.id},{"$push" :{"inventory" : {"name": skin_name, "float": final_float}}})

                    e.colour = discord.colour.Color.green()
                    e.set_footer(text="")
                    await  msg.edit(embed=e, view=None)
                else:
                    await interact.response.send_message("Your inventory is full! Sell an item or buy more inventory space")
            else:
                await interact.response.defer()

        async def sell_item():
            nonlocal user, is_sold
            #change color to green, remove footer, change balance to have balance of skin
            e.colour = discord.colour.Color.dark_gray()
            e.set_footer(text="")

            await msg.edit(embed=e, view=None)
            database.user_data.find_one_and_update({"_id": ctx.author.id}, {"$inc" :{"balance" : skin_price}})
            is_sold = True
               
        #call back for selling the item
        async def sell_callback(interact):
            if ctx.author.id == interact.user.id:
                await sell_item()
            else:
                await interact.response.defer()

        #set callabcks
        sell.callback = sell_callback
        inventory.callback = inventory_callback

        msg = await ctx.send(embed=e, view=view)

        await asyncio.sleep(30)
        if not is_sold:
            await sell_item()

    @commands.command(description="Take a chance to upgrade your skin to one of higher value", usage=f"""
    `{PREFIX}open <inventory item number> <item to recieve>`
    **Arguments**
    `<inventory item slot>` - the inventory slot number of the item you want to upgrade
    `<item to recieve>` - the name of the item you want to upgrade too
    """)
    async def upgrade(self, ctx, inventory_index:int, *args):
        pass


# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(Unboxing(bot))