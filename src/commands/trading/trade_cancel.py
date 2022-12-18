from discord.ext.commands import Context
from src.util.constants import PREFIX
from src.util import database

async def cancel(ctx:Context):
    delete_reuslt = database.trade_requests.delete_one({"_id": ctx.author.id, "send-timestamp": 0})
    successful = delete_reuslt.deleted_count >= 1

    if successful:
        await ctx.send("Successfully cancelled current trade")
    else:
        await ctx.send(f"You have no trade in creation! Use `{PREFIX}trade new <user>` to start a new trade")