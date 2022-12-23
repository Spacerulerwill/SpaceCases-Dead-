# This cog is for skin unboxing related commands
# Commands:
# * trade
# ** add
# ** remove
import discord
from discord.ext import commands
from discord.ext.commands import Context

from src.commands.trading.trade import view_trade_in_creation
from src.commands.trading.trade_new import new
from src.commands.trading.trade_cancel import cancel
from src.commands.trading.trade_add import add
from src.commands.trading.trade_remove import remove
from src.commands.trading.trade_send import send

from typing import Literal

# initialise class
class Trading(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def trade(self, ctx:Context):
        if ctx.invoked_subcommand is None:
            await view_trade_in_creation(ctx)

    @trade.command()
    async def new(self, ctx:Context, member:discord.Member):
        await new(ctx, member)

    @trade.command()
    async def cancel(self, ctx:Context):
        await cancel(ctx)

    @trade.command()
    async def send(self, ctx:Context):
        await send(ctx)

    @trade.command()
    async def add(self, ctx:Context, in_out:Literal["in", "out"], item_index:int):
        await add(ctx, in_out, item_index)
        
    @trade.command()
    async def remove(self, ctx:Context, in_out:Literal["in", "out"], item_index:int):
        await remove(ctx, in_out, item_index)
    

# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot:commands.Bot):
    await bot.add_cog(Trading(bot))