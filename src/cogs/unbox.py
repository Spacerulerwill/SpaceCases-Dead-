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
    @commands.command(description="View details for an item", usage=
    {
        "Syntax": f"`{PREFIX}item <item name>`",
        "Arguments": "`<item name>` - name of the item",
        "Item name formatting": 
        """
        Weapons: `<modifier> <condition> <weapon> <skin name>`
        """,
        "Examples": f"""
        `{PREFIX}item stattrak minimal wear mp7 bloodsport`
        `{PREFIX}item well worn bayonet lore`
        `{PREFIX}item souvenir field tested ak 47 green laminate`
        """
    }
    )
    async def item(self, ctx:Context, *args):
        await item(ctx, *args)

    # view a containers price and contents
    @commands.command(description="View a container's price and contents", usage=
    {
        "Syntax": f"`{PREFIX}container <container name>`",
        "Arguments": "`<container name>` - container name"
    })
    async def container(self, ctx:Context, *args):
        await container(ctx, *args)

    # see a list of all containers
    @commands.command(description="See a list of all purchasable containers", usage=
    {
        "Syntax": f"`{PREFIX}containers`"
    })
    async def containers(self, ctx:Context, page:int = 1):
        await containers(ctx, page)

    # open a container
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(description="Purchase and open a container, with the option to either sell the item unboxed or add it to your inventory", usage=
    {
        "Syntax": f"`{PREFIX}open <container name>`",
        "Arguments": "`<container name>` - the name of the container to open"
    })
    async def open(self, ctx:Context, *args):
        await open(ctx, *args)

    #upgrade a weapon
    @commands.command(description="Upgrade a weapon in your inventory to one of higher value", usage=
    {
        "Syntax": f"`{PREFIX}upgrade <item index> <result item>`",
        "Arguments": """
        `<item index>` - inventory index of the item you want to upgrade
        `<result item>` - the name of the item you want to upgrade too
        """,
        "Example": f"`{PREFIX}upgrade 1 stattrak minimal wear mp7 bloodsport`"
    })
    async def upgrade(self, ctx:Context, item_index:int, *args):
        await upgrade(ctx, item_index, *args)
    
# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(Unboxing(bot))