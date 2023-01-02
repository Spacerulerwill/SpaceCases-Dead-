import discord
from discord.ext.commands import Context
from src.util import database
from src.util.constants import PREFIX
from src.util.embed_func import msg_embed
from src.commands.trading.trade_func import send_trade_in_creation_embed, send_trade_notif_to_user
from src.util.decorators import requires
import time

@requires(users_registered=True)
async def send(ctx:Context):
    
    trade = database.trade_requests.find_one({"_id": ctx.author.id, "send-timestamp": 0})
    if trade is None:
        await msg_embed(ctx, f"You have no trade in creation! Use `{PREFIX}trade new <user>` to start a new trade")
        return

    update_result = database.trade_requests.update_one(
        {"_id": ctx.author.id, "send-timestamp": 0},
        {
            "$set": {
                "send-timestamp": int(time.time())
            }
        }
    )

    if update_result.matched_count == 0 or update_result.modified_count == 0:
        await msg_embed(ctx, f"You have no trade in creation! Use `{PREFIX}trade new <user>` to start a new trade")
        return

    recipient:discord.Member = await ctx.bot.fetch_user(trade["recipient-id"])
    await send_trade_notif_to_user(ctx.author, recipient)
    await send_trade_in_creation_embed(ctx, recipient, trade, True)