# This cog is for skin unboxing related commands
# Commands:
# * trade
# ** add
# ** remove
import discord
from discord.ext import commands
from discord.ext.commands import Context
from src.util.constants import PREFIX

#command
from src.commands.trading.trade import trade
from src.commands.trading.add import add
from src.commands.trading.remove import remove

# initialise class
class Trading(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    # initialise a trade
    @commands.group(description="Setup a trade request to send to another user", usage=f"""
    `{PREFIX}trade <recipient>`
    **Arguments**
    `<recipient>` - cthe name of the recipient of the trade request
    """, 
    invoke_without_command=True)
    async def trade(self, ctx:Context, member:discord.Member):
        if ctx.invoked_subcommand is None:
            await trade(ctx, self.bot, member)

    @trade.command()
    async def add(self, ctx:Context, item_index:int):
        await add(ctx, item_index)

    @trade.command()
    async def remove(self, ctx:Context, item_index:int):
        await remove(ctx,item_index)

# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot:commands.Bot):
    await bot.add_cog(Trading(bot))