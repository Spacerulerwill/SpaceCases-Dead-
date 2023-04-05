"""
Trading Command Cog
~~~~~~~~~~~~~~~~~~~

This cog contains the commands:
* Trade
  * New
  * Cancel
  * Send
  * Add
  * Remove
  * In
  * Out
* Trades
"""

import discord
from discord.ext import commands
from discord.ext.commands import Context
from src.util.constants import PREFIX

from src.commands.trading.trade import view_trade_in_creation
from src.commands.trading.trade_new import new
from src.commands.trading.trade_cancel import cancel
from src.commands.trading.trade_add import add
from src.commands.trading.trade_remove import remove
from src.commands.trading.trade_send import send
from src.commands.trading.trades import trades
from src.commands.trading.trade_in import view_incoming_trade
from src.commands.trading.trade_out import view_outgoing_trade
from src.commands.trading.trade_decline import decline
from src.commands.trading.trade_accept import accept

from typing import Literal, Optional


# initialise class
class Trading(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group()
    async def trade(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            await view_trade_in_creation(ctx)

    @trade.command()
    async def new(self, ctx: Context, member: discord.Member):
        await new(ctx, member)

    @trade.command()
    async def cancel(self, ctx: Context, recipient: discord.Member = None):
        await cancel(ctx, recipient)

    @trade.command()
    async def send(self, ctx: Context):
        await send(ctx)

    @trade.command()
    async def add(self, ctx: Context, in_out: Literal["in", "out"], item_index: int):
        await add(ctx, in_out, item_index)

    @trade.command()
    async def remove(self, ctx: Context, in_out: Literal["in", "out"], item_index: int):
        await remove(ctx, in_out, item_index)

    @commands.command()
    async def trades(
        self,
        ctx: Context,
        in_out: Optional[Literal["in", "out", "all"]],
        page: Optional[int] = 1,
    ):
        await trades(ctx, in_out, page)

    @trade.command()
    async def incoming(self, ctx: Context, sender: discord.Member):
        await view_incoming_trade(ctx, sender)

    @trade.command()
    async def out(self, ctx: Context, recipient: discord.Member):
        await view_outgoing_trade(ctx, recipient)

    @trade.command()
    async def accept(self, ctx: Context, sender: discord.Member):
        await accept(ctx, sender)

    @trade.command()
    async def decline(self, ctx: Context, sender: discord.Member):
        await decline(ctx, sender)


# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot: commands.Bot):
    await bot.add_cog(Trading(bot))
