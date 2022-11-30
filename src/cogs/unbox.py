# This cog is for skin unboxing related commands
# Commands:
# * item
# * container
# * containers

import discord
from discord.ext import commands
from discord.ext.commands import Context
from src.util.constants import PREFIX

from typing import Optional

#command
from src.commands.unbox.item import item
from src.commands.unbox.containers import containers
from src.commands.unbox.container import container
from src.commands.unbox.open import open

# initialise class
class Unboxing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # inspect a skins image and information
    @commands.command(description="View details for an item", usage=f"""
    `{PREFIX}item <item name>`
    **Arguments**
    `<item name>` - item name as a string
    **Additional Information**
    Different items have different naming conventions, such as:
    `Weapons - <modifier> <condition> <weapon name> <skin name>`
    """)
    async def item(self, ctx:Context, *args):
        await item(ctx, *args)

    # view a containers price and contents
    @commands.command(description="View a container's price and contents", usage=f"""
    `{PREFIX}container <container name>`
    **Arguments**
    `<container name>` - container name as a string
    """)
    async def container(self, ctx:Context, *args):
        await container(ctx, *args)

    # see a list of all containers
    @commands.command(description="See a list of all purchasable containers", usage=f"""
    `{PREFIX}containers`
    """)
    async def containers(self, ctx:Context, page:int = 1):
        await containers(ctx, page)

    @containers.error
    async def containers_error(self, ctx:Context, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Incorrect Arguments!")

    # open a container
    @commands.command(description="Purchase and open a container, with the option to either sell the item unboxed or add it to your inventory", usage=f"""
    `{PREFIX}open <container name>`
    **Arguments**
    `<container name>` - the name of the container to open as a string
    """)
    async def open(self, ctx:Context, *args):
        await open(ctx, *args)

# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(Unboxing(bot))