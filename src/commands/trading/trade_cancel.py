import discord
from discord.ext.commands import Context
from src.util.constants import PREFIX
from src.util import database
from src.util.decorators import requires
from src.util.embed_func import msg_embed

@requires(users_registered=True)
async def cancel(ctx:Context, recipient:discord.Member):
    # if recipient is None cancel the current trade in creation
    if recipient is None:
        delete_result = database.trade_requests.delete_one({"_id": ctx.author.id, "send-timestamp": 0})
        successful = delete_result.deleted_count >= 1

        if successful:
            await msg_embed(ctx, "Successfully cancelled current trade")
        else:
            await msg_embed(ctx, f"You have no trade in creation! Use `{PREFIX}trade new <user>` to start a new trade")
    else: # if a recipient is provided trade to that user
        delete_result = database.trade_requests.delete_one({"_id": ctx.author.id, "recipient-id": recipient.id})
        successful = delete_result.deleted_count >= 1

        if successful:
            await msg_embed(ctx, f"Successfully cancelled trade to {recipient.name}")
        else:
            await msg_embed(ctx, f"You have no outgoing trade with {recipient.name}")