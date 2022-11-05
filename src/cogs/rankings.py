# This cog is for skin unboxing related commands
# Commands:
# help

import discord
from discord.ext import commands
from src.util.constants import PREFIX
from src.util import database
from heapq import nlargest
from decimal import Decimal
from src.util.constants import MAX_THREADS
import concurrent.futures
import asyncio

# initialise class
class Rankings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="See your ranking in the global leaderboard", usage=f"""
    `{PREFIX}ranking <user>
    **Arguments**
    `<user>` - optional - user to check ranking of`
    """)
    async def ranking(self, ctx):
        user = database.user_data.find_one({"_id": ctx.author.id})

        if user == None:
            await ctx.send(f"You aren't registed! Use `{PREFIX}register` to register")
            return

        cursor = database.user_data.find({})

        inventory_values = []

        # get all user inventory values and put them in dict
        for document in cursor:
            inventory_value = 0
            for item in list(document["inventory"]):
                inventory_value += database.skin_data[item["name"]]["price"]
            inventory_values.append(inventory_value)
        
        #find authors inventory value
        author_inventory_value = 0
        for item in user["inventory"]:
            author_inventory_value += database.skin_data[item["name"]]["price"]

        #find amount of user inventory values less than than authors
        greater_than = 0
        for value in inventory_values:
            if value > author_inventory_value:
                greater_than += 1

        await ctx.send(f"You are ranked #{greater_than+1} on the global leaderboard")

    @commands.command(description="View the leaderboard for inventory value", usage=f"""
    `{PREFIX}leaderboard <page number>
    **Arguments**
    `<page number>` - defaults to 1 - leaderboard page number`
    """)
    async def leaderboard(self, ctx, page:int=1):

        amount_of_users = database.user_data.count_documents({})
        amount_of_pages = -(amount_of_users // -10) #equivalent to ceil division

        if page < 1 or page > amount_of_pages:
            await ctx.send("Invalid page number!")
            return

        async def id_name(id):
            nonlocal id_name_dict
            name = str(await self.bot.fetch_user(id))
            id_name_dict[id] = name

        page -= 1

        cursor = database.user_data.find({})

        inventory_value_dict = {}

        for document in cursor:
            inventory_value = 0
            for item in list(document["inventory"]):
                inventory_value += database.skin_data[item["name"]]["price"]
            inventory_value_dict[inventory_value] = document["_id"]

        id_name_dict = {}
        ordered_prices = sorted(inventory_value_dict, reverse=True)[page*10:(page+1)*10-1]
        leaderboard_data = {ordered_price: inventory_value_dict[ordered_price] for ordered_price in ordered_prices}
        tasks = [id_name(id) for id in leaderboard_data.values()]
        await asyncio.gather(*tasks)

        leaderboard_str = ""
        for count, (price, id) in enumerate(leaderboard_data.items()):
            price = str((Decimal(price) / 100).quantize(Decimal('0.01')))
            leaderboard_str += f"**{page * 10 + count+1})** {id_name_dict[id]}: ${price}\n"

        e = discord.Embed(title=f"Leaderboard - Page {page+1}/{amount_of_pages}", description=leaderboard_str)

        await ctx.send(embed=e)

    @leaderboard.error
    async def leaderboard_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Page number must be an integer!")

# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(Rankings(bot))