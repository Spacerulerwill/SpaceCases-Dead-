import discord
from src.util import database
from src.util.constants import PREFIX
from discord.ext.commands import Context
from src.commands.trading.trade_func import send_trade_in_creation_embed

async def view_trade_in_creation(ctx:Context):
    trade = database.trade_requests.find_one({"_id": ctx.author.id, "send-timestamp":0})
    if trade is None:
        await ctx.send(f"You have no trade in creation! Use `{PREFIX}trade new <user>` to start a new trade")
        return

    recipient = await ctx.bot.fetch_user(trade["recipient-id"])
    await send_trade_in_creation_embed(ctx, recipient, trade)