import discord
from datetime import datetime
from discord.ext.commands import Context
from src.util import database
from src.lang.lang import get_locale_fm
from src.util.embed_func import msg_embed
from src.commands.trading.trade_func import (
    send_trade_in_creation_embed,
    send_trade_notif_to_user,
)
from src.util.decorators import requires


@requires(users_registered=True)
async def send(ctx: Context):
    lang = database.user_data.find_one({"_id": ctx.author.id})["lang"]
    trade = database.trade_requests.find_one(
        {"_id": ctx.author.id, "send_timestamp": 0}
    )
    if trade is None:
        await msg_embed(ctx, get_locale_fm(lang, "no_trade_in_creation"))
        return

    update_result = database.trade_requests.update_one(
        {"_id": ctx.author.id, "send_timestamp": 0},
        {"$set": {"send_timestamp": datetime.utcnow()}},
    )

    if update_result.matched_count == 0 or update_result.modified_count == 0:
        await msg_embed(ctx, get_locale_fm(lang, "no_trade_in_creation"))
        return

    recipient: discord.Member = await ctx.bot.fetch_user(trade["recipient_id"])
    await send_trade_notif_to_user(lang, ctx.author, recipient)
    await send_trade_in_creation_embed(lang, ctx, recipient, trade, True)
