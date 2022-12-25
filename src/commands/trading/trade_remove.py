from discord.ext.commands import Context
from src.util import database
from src.commands.trading.trade_func import send_trade_in_creation_embed
from src.util.constants import PREFIX
from pymongo.errors import WriteError

async def remove(ctx:Context, in_out:str, item_index:int):
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
            update_result = database.trade_requests.update_one({"_id": ctx.author.id, "send-timestamp": 0}, [
                {"$set": {"sender-items": {
                    "$concatArrays": [ 
                            {"$slice": ["$sender-items", item_index]}, 
                            {"$slice": ["$sender-items", {"$add": [1, item_index]}, {"$size": "$sender-items"}]}
                    ]
                }}}
            ])
        except WriteError:
            await ctx.send(f"No item exists at index {item_index+1}")
            return


        if update_result.matched_count == 0:
            await ctx.send(f"You have no trade in creation! Use `{PREFIX}trade new <user>` to start a new trade")
            return

        if update_result.modified_count == 0:
            await ctx.send(f"No item exists at index {item_index+1}")
            return

    if in_out == "in":
        try:
            update_result = database.trade_requests.update_one({"_id": ctx.author.id, "send-timestamp": 0}, [
                {"$set": {"recipient-items": {
                    "$concatArrays": [ 
                            {"$slice": ["$recipient-items", item_index]}, 
                            {"$slice": ["$recipient-items", {"$add": [1, item_index]}, {"$size": "$recipient-items"}]}
                    ]
                }}}
            ])
        except WriteError:
            await ctx.send(f"No item exists at index {item_index+1}")
            return

        if update_result.matched_count == 0:
            await ctx.send(f"You have no trade in creation! Use `{PREFIX}trade new <user>` to start a new trade")
            return

        if update_result.modified_count == 0:
            await ctx.send(f"No item exists at index {item_index+1}")
            return

    recipient = await ctx.bot.fetch_user(trade["recipient-id"])
    await send_trade_in_creation_embed(ctx, recipient)
