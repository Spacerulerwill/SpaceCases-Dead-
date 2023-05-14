"""
Copyright (C) 2022 William Redding - All Rights Reserved

Commands
~~~~~~~~
* inventory
* inspect
* sell

See end of file for licence details
"""

import discord
from discord.ext import commands
from discord.ext.commands import Context
from discord.ext.commands.bot import Bot

from typing import Optional

# command imports
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
async def setup(bot: Bot):
    await bot.add_cog(Inventory(bot))


"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
