import discord
from discord.ext.commands import Context
from src.util import database
from src.util.constants import PREFIX
from src.commands.trading.trade import send_trade_embed

async def add(ctx:Context, in_out:str, item_index:int):
    user_data = database.user_data.find_one({"_id": ctx.author.id})
    if user_data is None:
        await ctx.send(f"You are not registered! Use `{PREFIX}register` to register")
        return

    trade = database.trade_requests.find_one({"_id": ctx.author.id, "send-timestamp": 0})
    if trade is None:
        await ctx.send(f"You have no trade in creation! Use `{PREFIX}trade new <user>` to start a new trade")
        return

    item_index -= 1

    if in_out == "out":
        try:
            update_result = database.trade_requests.update_one(
                {"_id": ctx.author.id, "send-timestamp": 0},
                {
                    "$addToSet": {
                        "sender-items": user_data["inventory"][item_index]
                    }
                }
            )
            if update_result.matched_count == 0:
                await ctx.send(f"You have no trade in creation! Use `{PREFIX}trade new <user>` to start a new trade")
                return
            if update_result.modified_count == 0:
                await ctx.send(f"You cannot add the same item twice to a trade!")
                return
        except IndexError:
            await ctx.send(f"No item exists in your inventory at index {item_index}")
            return
    
    if in_out == "in":
        
        recipient:discord.Member = await ctx.bot.fetch_user(trade["recipient-id"])
        recipient_data = database.user_data.find_one({"_id": recipient.id})
        try:
            update_result = database.trade_requests.update_one(
                {"_id": ctx.author.id, "send-timestamp": 0},
                {
                    "$addToSet": {
                        "recipient-items": recipient_data["inventory"][item_index]
                    }
                }
            )
            if update_result.matched_count == 0:
                await ctx.send(f"You have no trade in creation! Use `{PREFIX}trade new <user>` to start a new trade")
                return

            if update_result.modified_count == 0:
                await ctx.send(f"You cannot add the same item twice to a trade!")
                return

        except IndexError:
            await ctx.send(f"No item exists in {recipient.name}'s inventory at index {item_index+1}")
            return

    recipient = await ctx.bot.fetch_user(trade["recipient-id"])
    await send_trade_embed(ctx, recipient)
    
    