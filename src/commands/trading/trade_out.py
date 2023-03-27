import discord
from src.util import database
from src.util.lang import get_locale
from src.util.constants import PREFIX
from src.util.embed_func import msg_embed
from discord.ext.commands import Context
from src.commands.trading.trade_func import send_trade_embed
from src.util.decorators import requires

@requires(users_registered=True)
async def view_outgoing_trade(ctx:Context, recipient:discord.Member):
    lang = database.user_data.find_one({"_id": ctx.author.id})["language"]
    trade = database.trade_requests.find_one({"_id": ctx.author.id, "recipient-id": recipient.id, "send-timestamp": {"$ne": 0}})

    if trade is None:
        await msg_embed(ctx, get_locale(lang, "no_incoming_trade", recipient.name))
        return
        
    await send_trade_embed(lang, ctx, trade, False)