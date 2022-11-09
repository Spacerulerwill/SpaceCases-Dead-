# This cog is for skin unboxing related commands
# Commands:
# help

import discord
from discord.ext import commands
from src.util.constants import PREFIX
from src.util import database
from decimal import Decimal
from pymongo import ReturnDocument

def get_inventory_slot_price(user):
    return 100 * (user["inventory-size"]-5) ** 2 + 3000

STATIC_PRICE = "static"
DYNAMIC_PRICE = "dynamic"

shop_items_dict = {
    "inventory slot": {"type": DYNAMIC_PRICE, "func": get_inventory_slot_price, "mongo_field": "inventory-size", "mongo_operator": "$add", "mongo_operation": ["$inventory-size", 1]}
}

# initialise class
class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True, description="Open the shop menu to see what items are on sale", usage=f"""`{PREFIX}shop`""")
    async def shop(self, ctx):
        if ctx.invoked_subcommand is None:
            user = database.user_data.find_one({"_id": ctx.author.id})

            if user == None:
                await ctx.send(f"You aren't registed! Use `{PREFIX}register` to register")
                return
            
            e = discord.Embed(
                title="Shop", 
                description=
                f"""Select an item to buy!

                Use `{PREFIX}shop info <item name>` to see information about an items and `{PREFIX}shop buy <item name>` to buy one 
                """, 
                color=discord.Color.green()
            )
            
            #get item prices
            items_str = ""
            for item_name, item_data in shop_items_dict.items():
                if item_data["type"] == STATIC_PRICE:
                    item_price = "$" + str((Decimal(item_data["price"]) / 100).quantize(Decimal('0.01')))
                    items_str += f'{item_name.title()}: {item_price}'
                elif item_data["type"] == DYNAMIC_PRICE:
                    item_price = "$" + str((Decimal(item_data["func"](user)) / 100).quantize(Decimal('0.01')))
                    items_str += f'{item_name.title()}: {item_price}'

            e.add_field(name="Items For Sale", value=items_str)
            e.add_field(name="Balance", value="$" + str((Decimal(user["balance"])/100).quantize(Decimal('0.01'))))

            await ctx.send(embed=e)

    @shop.command(description="Get info about an item in the shop", usage=f"""`{PREFIX}shop info <item name>`
    **Arguments**
    `<item name>` - the name of the item you want to find more about
    """)
    async def info(self, ctx, *args):
        item_name = " ".join(args[:]).strip().lower()

    @info.error
    async def info_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Oops! You forgot to put the item name!")

    @shop.command(description="Buy an item from the shop", usage=f"""`{PREFIX}shop buy <item name>`
    **Arguments**
    `<item name>` - the name of the item you want to buy
    """)
    async def buy(self, ctx, *args):
        user = database.user_data.find_one({"_id": ctx.author.id})

        if user == None:
            await ctx.send(f"You aren't registed! Use `{PREFIX}register` to register")
            return

        item_name = " ".join(args[:]).strip().lower()

        if item_name not in shop_items_dict:
            await ctx.send("Item does not exist!")
            return
        
        item_data = shop_items_dict[item_name]

        if item_data["type"] == STATIC_PRICE:
            price = item_data["price"]
        elif item_data["type"] == DYNAMIC_PRICE:
            price = item_data["func"](user)

        # if have enough money, subtract from balance and increase inventory slot
        post_document = database.user_data.find_one_and_update({"_id": ctx.author.id},
        [
            {
                "$set": {                  
                    'balance': {
                        "$cond": {
                            "if": {
                                "$gte": ['$balance', price]
                            },
                            "then": {
                                "$subtract": [
                                    "$balance",
                                    price
                                ],
                            },
                            "else": "$balance"
                        }
                    },
                    item_data["mongo_field"]: {
                        "$cond": {
                            "if": {
                                "$gte": ['$balance', price]
                            },
                            "then": {
                                item_data["mongo_operator"]: item_data["mongo_operation"]
                            },
                            "else": "$" + item_data["mongo_field"]
                        }
                    }
                }
            },
        ],
        return_document=ReturnDocument.AFTER)

        # if no change has taken place
        if post_document[item_data["mongo_field"]] == user[item_data["mongo_field"]]:
            await ctx.send("Not enough balance to perform this action")
        else:
            await self.shop(ctx)

    @buy.error
    async def buy_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Oops! You forgot to put the item name!")

# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(Shop(bot))