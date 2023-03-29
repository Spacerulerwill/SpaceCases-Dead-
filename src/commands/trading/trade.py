from src.util import database
from src.util.lang import get_locale
from src.util.constants import PREFIX
from src.util.embed_func import msg_embed
from discord.ext.commands import Context
from src.commands.trading.trade_func import send_trade_in_creation_embed
from src.util.decorators import requires

@requires(users_registered=True)
async def view_trade_in_creation(ctx:Context):
    lang = database.user_data.find_one({"_id": ctx.author.id})["lang"]
    trade = database.trade_requests.find_one({"_id": ctx.author.id, "send_timestamp":0})
    if trade is None:
        await msg_embed(ctx, get_locale(lang, "no_trade_in_creation", PREFIX))
        return

    recipient = await ctx.bot.fetch_user(trade["recipient_id"])
    await send_trade_in_creation_embed(lang, ctx, recipient, trade)