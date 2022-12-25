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

#command
from src.commands.unbox.item import item
from src.commands.unbox.containers import containers
from src.commands.unbox.container import container
from src.commands.unbox.open import open
from src.commands.unbox.upgrade import upgrade

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

    #upgrade a weapon
    @commands.command(description="Upgrade a weapon in your inventory to one of higher value", usage=f"""
    `{PREFIX}upgrade <item index> <result item>`
    **Arguments**
    `<item index>` - the index of the item in your inventory you want to upgrade
    `<result item>` - the name of the item you want to upgrade too
    """)
    async def upgrade(self, ctx:Context, item_index:int, *args):
        await upgrade(ctx, item_index, *args)

    @upgrade.error
    async def containers_error(self, ctx:Context, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Incorrect Arguments!")
        if isinstance(error, commands.MissingRequiredArgument):
            error:commands.MissingRequiredArgument
            if error.param.name == "item_index":
                await ctx.send("Oops! You forgot to supply an item index")
            elif error.param.name == "result_item":
                await ctx.send("Oops! You forgot to supply the result item")

# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(Unboxing(bot))