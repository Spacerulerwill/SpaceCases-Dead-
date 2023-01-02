"""
Inventory Command Cog
~~~~~~~~~~~~~~~~~~~

This cog contains the commands:
* Inventory
* Inspect
* Sell
"""

import discord
from discord.ext import commands
from discord.ext.commands import Context
from src.util.constants import PREFIX

from typing import Optional

#command
from src.commands.inventory.inventory import inventory
from src.commands.inventory.inspect import inspect
from src.commands.inventory.sell import sell

# initialise class
class Inventory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # open inventory
    @commands.command(description="See someones inventory", usage=f"""
    `{PREFIX}inventory <user> <page>`
    **Arguments**
    `<user>` - optional - the owner of the inventory
    `<page>` - optional - the page of the inventory
    """,
    aliases=["inv"])
    async def inventory(self, ctx:Context, member:Optional[discord.Member]=None, page:Optional[int]=1):
        await inventory(ctx, member, page)

    @inventory.error
    async def inventory_error(self, ctx:Context, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Incorrect Arguments!")

    @commands.command(description="Inspect an item in someone's inventory", usage=f"""
    `{PREFIX}inspect <user> <item index>`
    **Arguments**
    `<user>` - optional - the user whos inventory you wish to look in
    `<item index>` - the index of the item
    """)
    async def inspect(self, ctx:Context, member:Optional[discord.Member]=None, item_index:int=None):
        await inspect(ctx, member, item_index)

    @inspect.error
    async def inspect_error(self, ctx:Context, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Incorrect Arguments!")

    @commands.command(description="Sell an item from your inventory", usage=f"""
    `{PREFIX}sell <item index>`
    **Arguments**
    `<item index>` - the index of the item you want to sell
    """)
    async def sell(self, ctx:Context, item_index:int):
        await sell(ctx, item_index)

    @sell.error
    async def sell_error(self, ctx:Context, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Incorrect Arguments!")

# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(Inventory(bot))