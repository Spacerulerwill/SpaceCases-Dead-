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

    @commands.group(
        invoke_without_command=True,
        description="Show your trade currently in creation",
        usage={"Syntax": f"`{PREFIX}trade`"},
    )
    async def trade(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            await view_trade_in_creation(ctx)

    @trade.command(
        description="Create a new trade with a user",
        usage={
            "Syntax": f"`{PREFIX}trade new <user>`",
            "Arguments": "`<user>` - user to initiate trade with",
        },
    )
    async def new(self, ctx: Context, member: discord.Member):
        await new(ctx, member)

    @trade.command(
        description="Cancel your current trade in creation or a trade already sent to a user",
        usage={
            "Syntax": f"`{PREFIX}trade cancel <user>`",
            "Arguments": """
        `<user>` - user to cancel trade to
        If no user is provided it will cancel your trade in creation
        """,
        },
    )
    async def cancel(self, ctx: Context, recipient: discord.Member = None):
        await cancel(ctx, recipient)

    @trade.command(
        description="Send your trade in creation to the recipient",
        usage={"Syntax": f"`{PREFIX}trade send`"},
    )
    async def send(self, ctx: Context):
        await send(ctx)

    @trade.command(
        description="Add an item to your trade in creation",
        usage={
            "Syntax": f"`{PREFIX}trade add in/out <inventory index>`",
            "Arguments": """
        `in/out` - whether the item is an incoming item or an outgoing item
        `<inventory index>` - inventory index of the item you want to add
        """,
        },
    )
    async def add(self, ctx: Context, in_out: Literal["in", "out"], item_index: int):
        await add(ctx, in_out, item_index)

    @trade.command(
        description="Remove an item from your trade in creation",
        usage={
            "Syntax": f"`{PREFIX}trade remove in/out <trade index>`",
            "Arguments": """
        `in/out` - whether the item is an incoming item or an outgoing item
        `<trade index>` - trade index of the item you want to add
        """,
        },
    )
    async def remove(self, ctx: Context, in_out: Literal["in", "out"], item_index: int):
        await remove(ctx, in_out, item_index)

    @commands.command(
        description="View your incoming or outgoing trade requests",
        usage={
            "Syntax": f"`{PREFIX}trades in/out/all`",
            "Arguments": "`in/out/all` - whether to view incoming, outgoing or all trades - **optional**",
        },
    )
    async def trades(
        self,
        ctx: Context,
        in_out: Optional[Literal["in", "out", "all"]],
        page: Optional[int] = 1,
    ):
        await trades(ctx, in_out, page)

    @trade.command(
        name="in",
        description="View an incoming trade request",
        usage={
            "Syntax": f"`{PREFIX}trade in <sender>`",
            "Arguments": "`<sender>` - the user who is sending the trade to you",
        },
    )
    async def incoming(self, ctx: Context, sender: discord.Member):
        await view_incoming_trade(ctx, sender)

    @trade.command(
        description="View an outgoing trade request",
        usage={
            "Syntax": f"`{PREFIX}trade out <recipient>`",
            "Arguments": "`<sender>` - the recipient of the trade",
        },
    )
    async def out(self, ctx: Context, recipient: discord.Member):
        await view_outgoing_trade(ctx, recipient)

    @trade.command(
        description="Accept a trade request from a user",
        usage={
            "Syntax": f"`{PREFIX}trade accept <sender>`",
            "Arguments": "`sender` - the user who sent you the trade",
        },
    )
    async def accept(self, ctx: Context, sender: discord.Member):
        await accept(ctx, sender)

    @trade.command(
        description="Decline a trade request",
        usage={
            "Syntax": f"`{PREFIX}trade decline <sender>`",
            "Arguments": "`sender` - the user who sent you the trade",
        },
    )
    async def decline(self, ctx: Context, sender: discord.Member):
        await decline(ctx, sender)


# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot: commands.Bot):
    await bot.add_cog(Trading(bot))
