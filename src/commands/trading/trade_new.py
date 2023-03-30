import discord
from discord.ext.commands import Context
from src.util import database
from src.util.lang import get_locale
from src.util.embed_func import msg_embed, msg_embed_response
from src.commands.trading.trade_func import send_trade_in_creation_embed
from pymongo.errors import DuplicateKeyError
from src.util.decorators import requires

from typing import Tuple


async def send_warning(lang: str, ctx: Context, recipient: discord.Member):
    e = discord.Embed(
        title=get_locale(lang, "trade_new.warning.embed.footer"),
        description=get_locale(lang, "trade_new.warning.embed.description"),
        color=discord.Color.red(),
    )
    e.set_thumbnail(url=ctx.author.display_avatar.url)
    e.set_footer(text=get_locale(lang, "trade_new.warning.embed.footer"))

    # callback funcs
    async def view_timeout_callback():
        await close_message()

    async def close_message():
        try:
            await msg.delete()
        except discord.errors.NotFound:
            pass

    async def cancel_callback(interact: discord.Interaction):
        if interact.user.id != ctx.author.id:
            await msg_embed_response(
                interact.response, get_locale(lang, "not_your_button"), ephemeral=True
            )
            return

        await close_message()

    async def continue_callback(interact: discord.Interaction):
        if interact.user.id != ctx.author.id:
            await msg_embed_response(
                interact.response, get_locale(lang, "not_your_button"), ephemeral=True
            )
            return

        trade = {
            "_id": ctx.author.id,
            "send_timestamp": 0,
            "recipient_id": recipient.id,
            "sender_items": [],
            "recipient_items": [],
            "send_timestamp": 0,
        }
        database.trade_requests.update_one(
            {"_id": ctx.author.id, "send_timestamp": 0}, {"$set": trade}, upsert=True
        )

        await close_message()
        await send_trade_in_creation_embed(lang, ctx, recipient, trade)

    view = discord.ui.View(timeout=30)
    view.on_timeout = view_timeout_callback

    continue_button = discord.ui.Button(
        label=get_locale(lang, "button.continue"), style=discord.ButtonStyle.green
    )
    continue_button.callback = continue_callback
    cancel_button = discord.ui.Button(
        label=get_locale(lang, "button.cancel"), style=discord.ButtonStyle.red
    )
    cancel_button.callback = cancel_callback
    view.add_item(continue_button)
    view.add_item(cancel_button)

    msg = await ctx.send(embed=e, view=view)


def try_create_trade_request(
    ctx: Context, recipient: discord.Member
) -> Tuple[bool, dict]:
    trade = {
        "_id": ctx.author.id,
        "recipient_id": recipient.id,
        "sender_items": [],
        "recipient_items": [],
        "send_timestamp": 0,
    }
    update_result = database.trade_requests.update_one(
        {"_id": ctx.author.id, "send_timestamp": 0},
        {"$setOnInsert": trade},
        upsert=True,
    )

    return update_result.upserted_id is not None, trade


@requires(users_registered=True)
async def new(ctx: Context, recipient: discord.Member):
    lang = database.user_data.find_one({"_id": ctx.author.id})["lang"]

    try:
        successful, trade = try_create_trade_request(ctx, recipient)
    except DuplicateKeyError:
        await msg_embed(
            ctx,
            get_locale(
                lang, "trade_error.already_have_trade_with_user", recipient.name
            ),
        )
        return

    if successful:
        # create new trade and show trade embed
        await send_trade_in_creation_embed(lang, ctx, recipient, trade)
    else:
        # show warning that this will override previous trade
        await send_warning(lang, ctx, recipient)
