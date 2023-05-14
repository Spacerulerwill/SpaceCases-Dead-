"""
Copyright (C) 2022 William Redding - All Rights Reserved

Commands
~~~~~~~~
* container
* containers
* item
* open
* upgrade
* tradeup

See end of file for licence details
"""

from discord.ext import commands
from discord.ext.commands import Context
from discord.ext.commands.bot import Bot

# command imports
from src.commands.unbox.item import item
from src.commands.unbox.containers import containers
from src.commands.unbox.container import container
from src.commands.unbox.open import open
from src.commands.unbox.upgrade import upgrade
from src.commands.unbox.tradeup import tradeup


# initialise class
class Unboxing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # inspect a skins image and information
    @commands.command()
    async def item(self, ctx: Context, *args):
        await item(ctx, *args)

    # view a containers price and contents
    @commands.command()
    async def container(self, ctx: Context, *args):
        await container(ctx, *args)

    # see a list of all containers
    @commands.command()
    async def containers(self, ctx: Context, page: int = 1):
        await containers(ctx, page)

    # open a container
    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command()
    async def open(self, ctx: Context, *args):
        await open(ctx, *args)

    # upgrade a weapon
    @commands.command()
    async def upgrade(self, ctx: Context, item_index: int, *args):
        await upgrade(ctx, item_index, *args)

    # trade up contract
    @commands.command()
    async def tradeup(self, ctx: Context, *args):
        await tradeup(ctx, *args)


# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot: Bot):
    await bot.add_cog(Unboxing(bot))

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