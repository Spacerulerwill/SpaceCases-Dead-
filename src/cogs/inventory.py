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

# command
from src.commands.inventory.inventory import inventory
from src.commands.inventory.inspect import inspect
from src.commands.inventory.sell import sell


# initialise class
class Inventory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["inv"])
    async def inventory(
        self,
        ctx: Context,
        member: Optional[discord.Member] = None,
        page: Optional[int] = 1,
    ):
        await inventory(ctx, member, page)

    @commands.command()
    async def inspect(
        self, ctx: Context, user: Optional[discord.Member], item_index: int
    ):
        await inspect(ctx, user, item_index)

    @commands.command()
    async def sell(self, ctx: Context, item_index: int):
        await sell(ctx, item_index)


# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(Inventory(bot))