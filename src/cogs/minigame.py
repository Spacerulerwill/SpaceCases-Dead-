# This cog is for skin unboxing related commands
# Commands:
# help

import discord
from discord.ext import commands
from src.util.constants import PREFIX
from src.util import database
import random

# initialise class
class Minigames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="50% chance to double your balance or lose it all!", usage=f"""
    `{PREFIX}double`
    """)
    async def double(self, ctx):
        user = database.user_data.find_one({"_id": ctx.author.id})

        if user == None:
            await ctx.send(f"You aren't registed! Use `{PREFIX}register` to register")
            return

        if user["balance"] == 0:
            await ctx.send("You have no balance, come back when you aren't broke!")
            return
        
        if random.random() < 0.5:
            database.user_data.find_one_and_update({"_id": ctx.author.id}, {"$inc" :{"balance" : user["balance"]}})
            await ctx.send("Congrats! Your balance has been doubled! 🥳")
        else:
            database.user_data.find_one_and_update({"_id": ctx.author.id}, {"$set" :{"balance" : 0}})
            await ctx.send("Unlucky! You have lost everything!") 


# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(Minigames(bot))