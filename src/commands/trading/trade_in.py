import discord
from src.util import database
from src.commands.trading.trade_func import send_trade_embed
from discord.ext.commands import Context
from src.util.decorators import requires

@requires(users_registered=True)
async def view_incoming_trade(ctx:Context, sender:discord.Member):
    trade = database.trade_requests.find_one({"_id": sender.id, "recipient-id": ctx.author.id, "send-timestamp": {"$ne": 0}})
    if trade is None:
        await ctx.send(f"You have no incoming trade from {sender.name}")
        return
        
    await send_trade_embed(ctx, trade, True)