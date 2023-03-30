import discord
from discord.ext.commands import Context
from src.util.constants import PREFIX
from src.util import database
from src.util.lang import get_locale
from src.util.decorators import requires
from src.util.embed_func import msg_embed


@requires(users_registered=True)
async def cancel(ctx: Context, recipient: discord.Member):
    lang = database.user_data.find_one({"_id": ctx.author.id})["lang"]
    # if recipient is None cancel the current trade in creation
    if recipient is None:
        delete_result = database.trade_requests.delete_one(
            {"_id": ctx.author.id, "send_timestamp": 0}
        )
        successful = delete_result.deleted_count >= 1

        if successful:
            await msg_embed(ctx, get_locale(lang, "trade_cancel.cancelled_current"))
        else:
            await msg_embed(ctx, get_locale(lang, "no_trade_in_creation", PREFIX))

    else:  # if a recipient is provided trade to that user
        delete_result = database.trade_requests.delete_one(
            {"_id": ctx.author.id, "recipient_id": recipient.id}
        )
        successful = delete_result.deleted_count >= 1

        if successful:
            await msg_embed(
                ctx,
                get_locale(
                    lang, "trade_cancel.cancelled_trade_to_user", recipient.name
                ),
            )
        else:
            await msg_embed(ctx, get_locale(lang, "no_outgoing_trade", recipient.name))
