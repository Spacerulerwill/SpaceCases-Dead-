# This cog is for skin unboxing related commands
# Commands:
# help

import discord
from discord.ext import commands
from src.util.constants import PREFIX

# initialise class
class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True, description="Open the shop menu to see what items are on sale", usage=f"""`{PREFIX}shop`""")
    async def shop(self, ctx):
        if ctx.invoked_subcommand is None:
            pass
        else:
            pass

    @shop.command(description="Buy an item for sale in the shop", usage=f"""`{PREFIX}shop buy <item number>`
    **Arguments**
    `<item number>` - the number of the item you want to buy
    """)
    async def buy(self, ctx, item_number:int):
        pass

    @buy.error
    async def buy_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Item number must be an integer!")
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Oops! You forgot to put the item number!")

# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(Shop(bot))