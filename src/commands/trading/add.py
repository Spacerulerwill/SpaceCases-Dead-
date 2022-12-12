import discord
from src.util import database
from src.util.constants import PREFIX
from discord.ext.commands import Context
from pymongo import ReturnDocument
from src.commands.trading.trade import send_trade_embed_view

async def add(ctx:Context, item_index:int):
    try:
        trade = database.user_trade_creation[ctx.author.id]
    except KeyError:
        pass # TODO add error message

    user_data = database.user_data.find_one({"_id": ctx.author.id})
    if user_data == None:
        # TODO error message
        return

    if trade["step"] == 1:
        sender_data = database.user_data.find_one({"_id": ctx.author.id})
        try:
            item = sender_data["inventory"][item_index-1]
            if item not in trade["sender_items"]:
                trade["sender_items"].append(item)
            else:
                # TODO error message
                pass
        except KeyError:
            # TODO no item exists at index
            return

    elif trade["step"] == 2:
        recipient_data = database.user_data.find_one({"_id": trade["recipient"]})
        try:        
            item = recipient_data["inventory"][item_index-1]
            if item not in trade["recipient_items"]:
                trade["recipient_items"].append(item)
            else:
                # TODO error message
                pass
        except KeyError:
            # TODO no item exists at index
            return

    recipient = await ctx.bot.fetch_user(trade["recipient"])
    await send_trade_embed_view(ctx, ctx.author, recipient)