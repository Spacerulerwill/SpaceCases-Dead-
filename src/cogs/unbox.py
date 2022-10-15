# This cog is for skin unboxing related commands
# Commands:
# * open
# * inspect

import discord
from discord.ext import commands
from discord import Embed
from src.util.constants import PREFIX, wear_dict, KEY_PRICE
from src.util import database
from src.util.format import remove_skin_name_formatting
from src.util.constants import case_rarity_odds, case_wear_ranges
import random
import requests
import urllib.parse

# initialise class
class UnboxCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # unbox a case 
    @commands.command()
    async def open(self, ctx, *args):
        # combine args to make word
        container_name = " ".join(args[:]).strip().lower()

        # get container price from steam market api and check if they have enough money to open
        case_market_hash_name = urllib.parse.quote(database.containers[container_name]["formatted_name"])
        container_req = requests.get(f"https://steamcommunity.com/market/priceoverview/?appid=730&currency=1&market_hash_name={case_market_hash_name}").json()

        user = database.user_data.find_one({"_id": ctx.author.id})

        if user == None:
            await ctx.send(f"Use {PREFIX}register to register!")
            return
        
        if container_req["success"]:
            container_price = float(container_req["median_price"][1:]) #remove dollar sign convert to float
            user_balance = user["balance"]

            #if they don't have enough
            if user_balance < container_price + KEY_PRICE:
                await ctx.send("Not enough balance to perform this action")
                return
            else: # if they do subtract from balance and continue
                new_balance = round(user_balance - (container_price + KEY_PRICE), 2)
                database.user_data.update_one(user,{"$set" :{"balance" : new_balance}})

        else:
            await ctx.send(f"Invalid case! Use {PREFIX}cases to see the list of available cases.")
            return

        #check container exists
        if container_name in database.containers:

            # get container
            container = database.containers[container_name]

            # get rarity
            rarity_rand = random.random()
            skin_rarity = None

            for rarity, upper in case_rarity_odds.items():
                if rarity_rand > upper:
                    skin_rarity = rarity
                    break
            
            # get skin
            skins_list = container[skin_rarity]
            skin_name = random.choice(skins_list)

            # float and condition
            min_float = database.csgostash_static_data[skin_name]["min_float"]
            max_float = database.csgostash_static_data[skin_name]["max_float"]

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
                    skin_wear = wear
                    break

            # create embed and show player
            formatted_name = database.csgostash_static_data[skin_name]["formatted_name"] + " " + skin_wear

            skin_name = skin_name + " " + remove_skin_name_formatting(skin_wear)
            
            image_url = database.skin_static_data[skin_name]["image_url"]
            color = int(database.skin_static_data[skin_name]["rarity_color"], base=16)
            skin_rarity = database.skin_static_data[skin_name]["rarity"]

            skin_price = database.skin_prices[skin_name]

            if skin_price == None or skin_price == 0:
                skin_price = 0

            e = Embed(title=formatted_name, color=color)
            e.add_field(name="Market Value", value="$" + "{:.2f}".format(skin_price))
            e.add_field(name="Rarity", value=skin_rarity)
            e.add_field(name="Float", value=str(final_float))
            e.add_field(name="New Balance", value="$" + "{:.2f}".format(new_balance))
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
                if ctx.author.id == interact.user.id:

                    e.colour = discord.colour.Color.green()
                    e.set_footer(text="")
                    await  msg.edit(embed=e, view=None)

            #call back for selling the item
            async def sell_callback(interact):
                nonlocal new_balance

                if ctx.author.id == interact.user.id:

                    #change color to green, remove footer, change balance to have balance of skin
                    e.colour = discord.colour.Color.dark_gray()
                    e.set_footer(text="")

                    new_balance = round(new_balance + skin_price, 2)
                    e.set_field_at(index=3, name="New Balance", value="$" + "{:.2f}".format(new_balance))
                    await msg.edit(embed=e, view=None)
                    database.user_data.update_one(user,{"$set" :{"balance" : new_balance}})

            sell.callback = sell_callback
            inventory.callback = inventory_callback

            msg = await ctx.send(embed=e, view=view)

        else:
            await ctx.send(f"Invalid case! Use {PREFIX}cases to see the list of available cases.")

    # view any weapon and see it's price
    @commands.command()
    async def inspect(self, ctx, *args):
        query = " ".join(args[:]).split(",")
        if not 3 <= len(query) <= 4:
            await ctx.send("Must provide 3 - 4 comma seperated arguments in format: weapon, skin name, condition, modifier: stattrak | souvenir (optional)")
            return

        #argument formatting to convert arguments to useable skin name
        query = [_s.strip() for _s in query]

        weapon = query[0]

        skin = query[1]

        unformatted_weapon = remove_skin_name_formatting(weapon)
        unformatted_skin = remove_skin_name_formatting(skin)
        unformatted_name = f"{unformatted_weapon} | {unformatted_skin}"            

        wear = query[2].lower()

        modifier = ""
        if len(query) == 4:
            modifier = query[3].lower()

        if unformatted_name not in database.csgostash_static_data:
            await ctx.send("Skin does not exist!")
            return
        else:
            if modifier not in database.csgostash_static_data[unformatted_name]:
                await ctx.send(f"Skin modifier can only be stattrak or souvenir")
                return
            else:
                if modifier == "stattrak":
                        modifier = "StatTrak™ "
                elif modifier == "souvenir":
                    modifier = "Souvenir"
                else:
                    await ctx.send(f"Skin not available as {modifier}")
                    return
        try:
            if database.csgostash_static_data[unformatted_name]["is_special"]:
                formatted_name = "★ " + modifier + database.csgostash_static_data[unformatted_name]["formatted_name"]
            else:
                formatted_name = modifier + database.csgostash_static_data[unformatted_name]["formatted_name"]
        except KeyError:
            await ctx.send(f"Skin does not exist!")
            return

        if wear not in wear_dict:
            await ctx.send(f"Wear must be one of the following: fn, mw, ft, ww, bs")
            return
        else:
            wear = wear_dict[wear]
            
        formatted_name = formatted_name + " " + wear

        full_name = remove_skin_name_formatting(formatted_name)

        # get price and details and create embed
        try:
            skin_price = database.skin_prices[full_name]
            if skin_price == None:
                skin_price = "Unknown"
            else:
                skin_price = "$" + "{:.2f}".format(skin_price)
        except:
            await ctx.send(f"Skin not available in that condition")
            return

        image_url = database.skin_static_data[full_name]["image_url"]
        color = int(database.skin_static_data[full_name]["rarity_color"], base=16)
        rarity = database.skin_static_data[full_name]["rarity"]
        
        e = Embed(title=formatted_name, color=color)
        e.add_field(name="Market Price", value=skin_price)
        e.add_field(name="Rarity", value=rarity, inline=True)

        if len(query) == 4 and query[3] == "souvenir":
            tournament = database.skin_static_data[full_name]["tournament"]
            e.add_field(name="Tournament", value=tournament)
            
        e.set_image(url=image_url)
        await ctx.send(embed=e)
        
# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(UnboxCommands(bot))