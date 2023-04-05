import discord
from src.util import database
from src.lang.lang import get_locale_fm
from src.util.string_util import currency_str_format
from src.util.embed_func import msg_embed, msg_embed_edit, msg_embed_response
from src.util.decorators import requires
from discord.ext.commands import Context


@requires(users_registered=True)
async def sell(ctx: Context, item_index: int):
    user_data = database.user_data.find_one({"_id": ctx.author.id})
    lang = user_data["lang"]
    user_inventory = list(user_data["inventory"])

    if item_index > len(user_inventory):
        await msg_embed(
            ctx, get_locale_fm(lang, "inventory.not_found_index", item_index)
        )
        return

    # callbacks
    is_msg_deleted = False

    async def close_message():
        nonlocal is_msg_deleted
        if not is_msg_deleted:
            is_msg_deleted = True
            await msg.delete()

    async def sell_callback(interact: discord.Interaction):
        if interact.user.id != ctx.author.id:
            await msg_embed_response(
                interact.response,
                get_locale_fm(lang, "not_your_button"),
                ephemeral=True,
            )
            return

        update_result = database.user_data.update_one(
            {"_id": ctx.author.id, "inventory": {"name": item, "float": float}},
            {
                "$pull": {"inventory": {"name": item, "float": float}},
                "$inc": {
                    "balance": database.skin_data["skins"][item]["price"],
                    "inventory_size": -1,
                },
            },
        )

        if update_result.matched_count == 0:
            await close_message()
            await msg_embed(
                ctx, get_locale_fm(lang, "sell.item_missing", formatted_name)
            )
        else:
            await msg_embed_edit(
                msg, get_locale_fm(lang, "sell.success", formatted_name), view=None
            )

    async def cancel_callback(interact: discord.Interaction):
        if interact.user.id != ctx.author.id:
            await msg_embed_response(
                interact.response,
                get_locale_fm(lang, get_locale_fm("not_your_button")),
                ephemeral=True,
            )
            return

        await close_message()

    item_index -= 1

    item = user_inventory[item_index]["name"]
    float = user_inventory[item_index]["float"]
    item_data = database.skin_data["skins"][item]
    formatted_name = item_data["formatted_name"]
    price = currency_str_format(item_data["price"])

    view = discord.ui.View(timeout=30)
    view.on_timeout = close_message
    confirm_button = discord.ui.Button(
        label=get_locale_fm(lang, "button.sell"), style=discord.ButtonStyle.green
    )
    confirm_button.callback = sell_callback

    cancel_button = discord.ui.Button(
        label=get_locale_fm(lang, "button.cancel"), style=discord.ButtonStyle.red
    )
    cancel_button.callback = cancel_callback

    view.add_item(confirm_button)
    view.add_item(cancel_button)

    msg = await msg_embed(
        ctx, get_locale_fm(lang, "sell.are_you_sure", formatted_name, price), view=view
    )
