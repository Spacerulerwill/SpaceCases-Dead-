from discord.ext.commands import Context
from src.util import database
from src.util.constants import PREFIX
from src.util.embed_func import msg_embed

async def register(ctx:Context):
    update_result = database.user_data.update_one(
        {"_id": ctx.author.id},
        {
            "$setOnInsert": {
                "balance": 0,
                "last-claim": 0,
                "claim-streak": 0,
                "inventory": [],
                "inventory-size": 0,
                "inventory-max-capacity": 5,
                "stats": {
                    "containers-opened": 0,
                    "total-spent": 0,
                    "total-return": 0,
                },
            }
        },
        upsert=True
    )

    if update_result.upserted_id == None:
        await msg_embed(ctx, "You are already registered!")
    else:
        await msg_embed(ctx, f"Registered! Use `{PREFIX}claim` to claim some money!")