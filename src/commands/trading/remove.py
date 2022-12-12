import discord
from src.util import database
from src.util.constants import PREFIX
from discord.ext.commands import Context
from src.commands.trading.trade import send_trade_embed_view

async def remove(ctx:Context, item_index:int):
    try:
        trade = database.user_trade_creation[ctx.author.id]
    except KeyError:
        pass # TODO add error message

    if trade["step"] == 1:
        try:
            del database.user_trade_creation[ctx.author.id]["sender_items"][item_index-1]
        except KeyError:
            # TODO no item exists at index
            return

    elif trade["step"] == 2:
        try:        
            del database.user_trade_creation[ctx.author.id]["recipient_items"][item_index-1]
        except KeyError:
            # TODO no item exists at index
            return

    recipient = await ctx.bot.fetch_user(trade["recipient"])
    await send_trade_embed_view(ctx, ctx.author, recipient)