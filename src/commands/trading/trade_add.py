import discord
from discord.ext.commands import Context
from src.util import database
from src.lang.lang import get_locale_fm
from src.commands.trading.trade_func import send_trade_in_creation_embed
from src.util.decorators import requires
from src.util.embed_func import msg_embed


@requires(users_registered=True)
async def add(ctx: Context, in_out: str, item_index: int):
    user_data = database.user_data.find_one({"_id": ctx.author.id})
    lang = user_data["lang"]

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
                {"$addToSet": {"sender_items": user_data["inventory"][item_index]}},
            )
            if update_result.matched_count == 0:
                await msg_embed(ctx, get_locale_fm(lang, "no_trade_in_creation"))
                return
            if update_result.modified_count == 0:
                await msg_embed(
                    ctx, get_locale_fm(lang, "trade_add.cannot_add_item_twice")
                )
                return
        except IndexError:
            await msg_embed(
                ctx, get_locale_fm(lang, "inventory.not_found_index", item_index + 1)
            )
            return

    if in_out == "in":
        recipient: discord.Member = await ctx.bot.fetch_user(trade["recipient_id"])
        recipient_data = database.user_data.find_one({"_id": recipient.id})
        try:
            update_result = database.trade_requests.update_one(
                {"_id": ctx.author.id, "send_timestamp": 0},
                {
                    "$addToSet": {
                        "recipient_items": recipient_data["inventory"][item_index]
                    }
                },
            )
            if update_result.matched_count == 0:
                await msg_embed(ctx, get_locale_fm(lang, "no_trade_in_creation"))
                return

            if update_result.modified_count == 0:
                await msg_embed(
                    ctx, get_locale_fm(lang, "trade_add.cannot_add_item_twice")
                )
                return

        except IndexError:
            await msg_embed(
                ctx, get_locale_fm(lang, "inventory.not_found_index", item_index + 1)
            )
            return

    recipient = await ctx.bot.fetch_user(trade["recipient_id"])
    await send_trade_in_creation_embed(lang, ctx, recipient)
