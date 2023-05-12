from discord.ext.commands import Context
from src.util import database
from src.lang.lang import get_locale_fm
from src.commands.trading.trade_func import send_trade_in_creation_embed
from src.util.embed_func import msg_embed
from pymongo.errors import WriteError
from src.util.decorators import requires


@requires(users_registered=True)
async def remove(ctx: Context, in_out: str, item_index: int):
    lang = database.user_data.find_one({"_id": ctx.author.id})["lang"]

    trade = database.trade_requests.find_one(
        {"_id": ctx.author.id, "send_timestamp": 0}
    )
    if trade is None:
        await msg_embed(ctx, get_locale_fm(lang, "no_trade_in_creation"))
        return

    item_index -= 1

    if in_out == "out":
        try:
            update_result = database.trade_requests.update_one(
                {"_id": ctx.author.id, "send_timestamp": 0},
                [
                    {
                        "$set": {
                            "sender_items": {
                                "$concatArrays": [
                                    {"$slice": ["$sender_items", item_index]},
                                    {
                                        "$slice": [
                                            "$sender_items",
                                            {"$add": [1, item_index]},
                                            {"$size": "$sender_items"},
                                        ]
                                    },
                                ]
                            }
                        }
                    }
                ],
            )
        except WriteError:
            await msg_embed(
                ctx, get_locale_fm(lang, "inventory.not_found_index", item_index + 1)
            )
            return

        if update_result.matched_count == 0:
            await msg_embed(ctx, get_locale_fm(lang, "no_trade_in_creation"))
            return

        if update_result.modified_count == 0:
            await msg_embed(
                ctx, get_locale_fm(lang, "inventory.not_found_index", item_index + 1)
            )
            return

    if in_out == "in":
        try:
            update_result = database.trade_requests.update_one(
                {"_id": ctx.author.id, "send_timestamp": 0},
                [
                    {
                        "$set": {
                            "recipient_items": {
                                "$concatArrays": [
                                    {"$slice": ["$recipient_items", item_index]},
                                    {
                                        "$slice": [
                                            "$recipient_items",
                                            {"$add": [1, item_index]},
                                            {"$size": "$recipient_items"},
                                        ]
                                    },
                                ]
                            }
                        }
                    }
                ],
            )
        except WriteError:
            await msg_embed(
                ctx, get_locale_fm(lang, "inventory.not_found_index", item_index + 1)
            )
            return

        if update_result.matched_count == 0:
            await msg_embed(ctx, get_locale_fm(lang, "no_trade_in_creation"))
            return

        if update_result.modified_count == 0:
            await msg_embed(
                ctx, get_locale_fm(lang, "inventory.not_found_index", item_index + 1)
            )
            return

    recipient = await ctx.bot.fetch_user(trade["recipient_id"])
    await send_trade_in_creation_embed(lang, ctx, recipient)