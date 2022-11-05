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
    `{PREFIX}ranking <user>`
    **Arguments**
    `<user>` - optional - user to check ranking of
    """)
    async def ranking(self, ctx, member:discord.Member = None):

        if member == None:
            member = ctx.author
            name = "You are "
        else:
            name = f"{member.display_name} is "

        member_data = database.user_data.find_one({"_id": member.id})

        if member_data == None:
            if member == ctx.author:
                await ctx.send(f"You aren't registed! Use `{PREFIX}register` to register")
            else:
                await ctx.send(f'{member.display_name} has not registered yet')
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
        member_inventory_value = 0
        for item in member_data["inventory"]:
            member_inventory_value += database.skin_data[item["name"]]["price"]

        #find amount of user inventory values great than than authors
        greater_than = 0
        for value in inventory_values:
            if value >= member_inventory_value:
                greater_than += 1

        await ctx.send(f"{name}ranked #{greater_than} on the global leaderboard")

    @ranking.error
    async def ranking_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Could not find that user!")

    @commands.command(description="View the leaderboard for inventory value", usage=f"""
    `{PREFIX}leaderboard <page number>`
    **Arguments**
    `<page number>` - defaults to 1 - leaderboard page number`
    """)
    async def leaderboard(self, ctx, page:int=1):

        amount_of_users = database.user_data.count_documents({})
        amount_of_pages = -(amount_of_users // -10) #equivalent to ceil division

        if page < 1 or page > amount_of_pages:
            await ctx.send("Invalid page number!")
            return

    @leaderboard.error
    async def leaderboard_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Page number must be an integer!")

# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(Rankings(bot))