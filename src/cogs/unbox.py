"""
Unbox Command Cog
~~~~~~~~~~~~~~~~~~~

This cog contains the commands:
* Item
* Container
* Containers
* Upgrade
* Open
"""

from discord.ext import commands
from discord.ext.commands import Context
from src.util.constants import PREFIX

# command
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
    async def tradeup(self, ctx: Context):
        await tradeup(ctx)


# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(Unboxing(bot))
