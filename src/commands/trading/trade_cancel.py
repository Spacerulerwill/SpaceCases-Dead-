import discord
from discord.ext.commands import Context
from src.util.constants import PREFIX
from src.util import database
from src.util.decorators import requires

@requires(users_registered=True)
async def cancel(ctx:Context, recipient:discord.Member):
    # if recipient is None cancel the current trade in creation
    if recipient is None:
        delete_result = database.trade_requests.delete_one({"_id": ctx.author.id, "send-timestamp": 0})
        successful = delete_result.deleted_count >= 1

        if successful:
            await ctx.send("Successfully cancelled current trade")
        else:
            await ctx.send(f"You have no trade in creation! Use `{PREFIX}trade new <user>` to start a new trade")
    else: # if a recipient is provided trade to that user
        delete_result = database.trade_requests.delete_one({"_id": ctx.author.id, "recipient-id": recipient.id})
        successful = delete_result.deleted_count >= 1

        if successful:
            await ctx.send(f"Successfully cancelled trade to {recipient.name}")
        else:
            await ctx.send(f"You have no outgoing trade with {recipient.name}")