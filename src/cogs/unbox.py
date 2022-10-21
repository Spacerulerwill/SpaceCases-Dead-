# This cog is for skin unboxing related commands
# Commands:
# * open
# * weapon
# * container
# * containers

import discord
from discord.ext import commands
from src.util.constants import PREFIX, wear_dict, KEY_PRICE
from src.util.format import remove_skin_name_formatting
from src.util.constants import conditions, rarity_color_dict, case_rarity_odds, case_wear_ranges
from src.util import database
import random
from decimal import Decimal


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
class UnboxCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def weapon(self, ctx, *args):
        weapon_query = " ".join(args[:]).strip().lower()

        if weapon_query not in database.skin_data:
            await ctx.send("Could not find weapon")
            return
        try:
            weapon_data = database.skin_data[weapon_query]

            formatted_name = weapon_data["formatted_name"]
            price = "$" + weapon_data["price"]

            image_url = weapon_data["image_url"]
            rarity = weapon_data["rarity"]
            rarity_color = rarity_color_dict[rarity]
            e = discord.Embed(title=formatted_name, color=rarity_color)
            e.add_field(name="Current Market Value", value=price)
            e.add_field(name="Rarity", value=rarity)
            e.set_image(url=image_url)

            await ctx.send(embed=e)
        except KeyError:
            await ctx.send("Could not find weapon")
            return

    @commands.command()
    async def container(self, ctx, *args):
        container = " ".join(args[:]).strip().lower()

        if container not in database.containers:
            await ctx.send("Invalid container!")
            return
        
        container_data = database.containers[container]

        container_image_url = container_data["image_url"]

        container_formatted_name = container_data["formatted_name"]

        container_item_data = container_data["items"]
        
        container_price = container_data["price"]

        #make a list of all items skins in case
        all_container_items = []
        for quality in container_item_data.values():
            all_container_items += quality

        items_amount = len(all_container_items)

        item_index = 0

        #create buttons for changing item
        view = discord.ui.View()
        prev_button = discord.ui.Button(label="◀", style=discord.ButtonStyle.gray)
        next_button = discord.ui.Button(label="▶", style=discord.ButtonStyle.gray)
        view.add_item(prev_button)
        view.add_item(next_button)

        async def next_button_callback(interaction):
            nonlocal item_index

            if interaction.user.id == ctx.author.id and item_index < len(all_container_items)-1:
                item_index += 1
                await msg.edit(embed=get_embed())

            await interaction.response.defer()

        async def prev_button_callback(interaction):
            nonlocal item_index

            if interaction.user.id == ctx.author.id and item_index > 0:
                item_index -= 1
                await msg.edit(embed=get_embed())

            await interaction.response.defer()

        next_button.callback = next_button_callback
        prev_button.callback = prev_button_callback

        #create a new embed for each item
        def get_embed(): 
            item = all_container_items[item_index]
            formatted_item_name = database.skin_data[item]["formatted_name"]
            best_condition_index = database.skin_data[item]["best_condition_index"]
            best_condition = conditions[best_condition_index].lower()
            item_data = database.skin_data[best_condition + " " + item]

            image_url = item_data["image_url"]
            rarity = item_data["rarity"]
            rarity_color = rarity_color_dict[rarity]
            min_float = "{:.2f}".format(item_data["min_float"])
            max_float ="{:.2f}".format(item_data["max_float"])

            best_condition_index = item_data["best_condition_index"]
            worst_condition_index = item_data["worst_condition_index"]

            has_stattrak_variant = item_data["has_stattrak_variant"]
            has_souvenir_variant = item_data["has_souvenir_variant"]

            has_modifier_price = False

            min_price = float('inf')
            max_price = 0.0
            for i in range(best_condition_index, worst_condition_index+1):
                price = Decimal(database.skin_data[conditions[i].lower() + " " + item]["price"]).quantize(Decimal('0.01'))
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
                    price = Decimal(database.skin_data[modifier + conditions[i].lower() + " " + item]["price"]).quantize(Decimal('0.01'))
                    if price < min_modifier_price:
                        min_modifier_price = price
                    if price > max_modifier_price:
                        max_modifier_price = price

            price_range_str = f"${min_price} - ${max_price}"
            if has_modifier_price: 
                price_range_str += f"\n${min_modifier_price} - ${max_modifier_price}"

            e = discord.Embed(title=f"{container_formatted_name} - ${container_price}\n{formatted_item_name} ({item_index+1}/{items_amount})", color=rarity_color)
            e.add_field(name="Rarity", value=rarity)
            e.add_field(name="Price Range", value=price_range_str)
            e.add_field(name="Float Range", value=f"{min_float} - {max_float}")
            e.set_image(url=image_url)
            e.set_thumbnail(url=container_image_url)
            return e

        msg = await ctx.send(embed=get_embed(), view=view)

    @commands.command()
    async def containers(self, ctx, page:int = 1):
        if page <= 0 or page > len_containerlist_pages:
            await ctx.send("Invalid page number!")
            return
        page -= 1
        page_title, page_fields = list(containerlist_pages.items())[page]
        e = discord.Embed(title=f"Page {page+1}/{len_containerlist_pages}")

        e.set_footer(text=f"Use {PREFIX}container (case name) to see a case's contents and {PREFIX}open to open one")

        for field in page_fields:
            e.add_field(name=page_title, value=field)

        await ctx.send(embed=e)

    @containers.error
    async def containerlist_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Page number must be an integer!")

    @commands.command()
    async def open(self, ctx, *args):
        container_name = " ".join(args[:]).strip().lower()
        
        if container_name not in database.containers:
            await ctx.send("Container does not exist!")
            return

        user = database.user_data.find_one({"_id": ctx.author.id})

        if user == None:
            await ctx.send(f"You aren't registed! Use {PREFIX}register to register")
            return

        container = database.containers[container_name]

        container_price = Decimal(container["price"])

        user_balance = Decimal(user["balance"])
        user_total_spent = Decimal(user["total-spent"])
        user_total_return = Decimal(user["total-return"])
        user_containers_opened = user["containers-opened"]

        #if they don't have enough
        if user_balance < container_price + KEY_PRICE:
            await ctx.send("Not enough balance to perform this action")
            return

        #subtract from balance, increase total spent, and containers opened
        new_balance = str(user_balance - (container_price + KEY_PRICE))
        new_total_spent = str(user_total_spent + container_price + KEY_PRICE)
        new_containers_opened = user_containers_opened + 1

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
        
        skin_price = Decimal(database.skin_data[skin_name]["price"]).quantize(Decimal('0.01')) # 2 dp

        new_total_return = str(user_total_return + skin_price)
        
        #update user data
        database.user_data.update_one(user,{"$set" :{"balance" : new_balance, "total-spent": new_total_spent, "total-return": new_total_return, "containers-opened": new_containers_opened}})

        e = discord.Embed(title=formatted_name, color=color)
        e.add_field(name="Market Value", value="$" + str(skin_price))
        e.add_field(name="Rarity", value=skin_rarity)
        e.add_field(name="Float", value=str(final_float))
        e.add_field(name="New Balance", value="$" + new_balance)
        e.set_image(url=image_url)
        e.set_footer(text="Warning! Buttons are only usable for 30 seconds.")

        #create buttons
        view = discord.ui.View(timeout=30)
        sell = discord.ui.Button(style=discord.ButtonStyle.red, label="Sell")
        inventory = discord.ui.Button(style=discord.ButtonStyle.green, label="Add to Inventory")
        view.add_item(item=sell)
        view.add_item(item=inventory)

        #call back for adding to inventory
        async def inventory_callback(interact):
            nonlocal user

            if ctx.author.id == interact.user.id:
                user = database.user_data.find_one({"_id": ctx.author.id})
                
                # add to inventory if there is room
                inventory = list(user["inventory"])

                if len(inventory) < user["inventory-size"]:
                    inventory.append({skin_name: final_float})

                    database.user_data.update_one(user,{"$set" :{"inventory" : inventory}})

                    e.colour = discord.colour.Color.green()
                    e.set_footer(text="")
                    await  msg.edit(embed=e, view=None)
                else:
                    await ctx.send("Your inventory is full! Sell an item or buy more inventory space")
                    await interact.response.defer()
               
        #call back for selling the item
        async def sell_callback(interact):
            nonlocal new_balance, user

            #refresh user document
            user = database.user_data.find_one({"_id": ctx.author.id})
            
            if ctx.author.id == interact.user.id:

                #change color to green, remove footer, change balance to have balance of skin
                e.colour = discord.colour.Color.dark_gray()
                e.set_footer(text="")

                new_balance = str(Decimal(new_balance) + skin_price)
                e.set_field_at(index=3, name="New Balance", value="$" + new_balance)
                await msg.edit(embed=e, view=None)
                database.user_data.update_one(user, {"$set" :{"balance" : new_balance}})

        #set callabcks
        sell.callback = sell_callback
        inventory.callback = inventory_callback

        msg = await ctx.send(embed=e, view=view)

# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(UnboxCommands(bot))