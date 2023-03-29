from discord.ext.commands import Context
from src.util import database
from src.util.lang import get_locale
from src.commands.trading.trade_func import send_trade_in_creation_embed
from src.util.constants import PREFIX
from src.util.embed_func import msg_embed
from pymongo.errors import WriteError
from src.util.decorators import requires

@requires(users_registered=True)
async def remove(ctx:Context, in_out:str, item_index:int):
    lang = database.user_data.find_one({"_id": ctx.author.id})["lang"]

    trade = database.trade_requests.find_one({"_id": ctx.author.id, "send-timestamp": 0})
    if trade is None:
        await msg_embed(ctx, get_locale(lang, "no_trade_in_creation", PREFIX))
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
            await msg_embed(ctx, get_locale(lang, "inventory.not_found_index", item_index+1))
            return


        if update_result.matched_count == 0:
            await msg_embed(ctx, get_locale(lang, "no_trade_in_creation", PREFIX))
            return

        if update_result.modified_count == 0:
            await msg_embed(ctx, get_locale(lang, "inventory.not_found_index", item_index+1))
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
            await msg_embed(ctx, get_locale(lang, "inventory.not_found_index", item_index+1))
            return

        if update_result.matched_count == 0:
            await msg_embed(ctx, get_locale(lang, "no_trade_in_creation", PREFIX))
            return

        if update_result.modified_count == 0:
            await msg_embed(ctx, get_locale(lang, "inventory.not_found_index", item_index+1))
            return

    recipient = await ctx.bot.fetch_user(trade["recipient-id"])
    await send_trade_in_creation_embed(lang, ctx, recipient)
