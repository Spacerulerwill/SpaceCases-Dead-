from discord.ext.commands import Context
from src.util import database
from src.util.constants import PREFIX, DEFAULT_INVENTORY_SIZE

async def register(ctx:Context):
    if database.user_data.find_one({"_id": ctx.author.id}) == None:
        database.user_data.insert_one({
            "_id": ctx.author.id,
            "balance": 0,
            "last-claim": 0,
            "inventory": [None for i in range(DEFAULT_INVENTORY_SIZE)],
            "inventory-size": 5,
            "containers-opened": 0,
            "total-spent": 0,
            "total-return": 0,
            "modified": False
        })
        await ctx.send(f"Registered! Use `{PREFIX}claim` to claim some money!")
    else:
        await ctx.send("You are already registered!")