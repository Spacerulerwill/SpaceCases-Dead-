from discord.ext.commands import Context
from src.util import database
from src.util.lang import get_locale
from src.util.constants import PREFIX
from src.util.embed_func import msg_embed
import time


async def register(ctx: Context):
    update_result = database.user_data.update_one(
        {"_id": ctx.author.id},
        {
            "$setOnInsert": {
                "join_date": int(time.time()),
                "balance": 0,
                "lang": "en",
                "last_claim": 0,
                "claim_streak": 0,
                "inventory": [],
                "inventory_size": 0,
                "inventory_max_capacity": 5,
                "stats": {
                    "containers_opened": 0,
                    "total_spent": 0,
                    "total_return": 0,
                },
            }
        },
        upsert=True,
    )

    if update_result.upserted_id == None:
        user_data = database.user_data.find_one({"_id": ctx.author.id})
        await msg_embed(
            ctx, get_locale(user_data["lang"], "register.already_registered")
        )
    else:
        await msg_embed(ctx, f"Registered! Use `{PREFIX}claim` to claim some money!")
