import discord
from src.util import database
from src.lang.lang import get_locale_fm
from src.util.embed_func import msg_embed
from discord.ext.commands import Context
from src.commands.trading.trade_func import send_trade_embed
from src.util.decorators import requires


@requires(users_registered=True)
async def view_outgoing_trade(ctx: Context, recipient: discord.Member):
    lang = database.user_data.find_one({"_id": ctx.author.id})["lang"]
    trade = database.trade_requests.find_one(
        {
            "_id": ctx.author.id,
            "recipient_id": recipient.id,
            "send_timestamp": {"$ne": 0},
        }
    )

    if trade is None:
        await msg_embed(ctx, get_locale_fm(lang, "no_incoming_trade", recipient.name))
        return

    await send_trade_embed(lang, ctx, trade, False)