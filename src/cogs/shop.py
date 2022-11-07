# This cog is for skin unboxing related commands
# Commands:
# help

import discord
from discord.ext import commands
from src.util.constants import PREFIX
from src.util import database

def get_inventory_slot_price(user):
    return 100 * (user["inventory-size"]-5) ** 2 + 3000

STATIC_PRICE = "static"
DYNAMIC_PRICE = "dynamic"

shop_items_dict = {
    "extra inventory slot": {"type": STATIC_PRICE, "func": get_inventory_slot_price}
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
            
            e = discord.Embed(title="Shop", description="Select an item to buy!", color=discord.Color.green())

            view = discord.ui.View()

            buy_button = discord.ui.Button(label="Buy", style=discord.ButtonStyle.green)

            view.add_item(buy_button)

            await ctx.send(embed=e, view=view)

    @shop.command(description="Get info about an item in the shop", usage=f"""`{PREFIX}shop info <item name>`
    **Arguments**
    `<item name>` - the name of the item you want to find more about
    """)
    async def info(self, ctx, *args):
        item_name = " ".join(args[:]).strip().lower()

    @info.error
    async def buy_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Oops! You forgot to put the item name!")

# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(Shop(bot))