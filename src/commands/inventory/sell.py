import discord
from src.util import database
from src.util.string_util import currency_str_format
from src.util.embed_func import msg_embed, msg_embed_edit
from src.util.decorators import requires
from discord.ext.commands import Context


@requires(users_registered=True)
async def sell(ctx:Context, item_index:int):
    user_data = database.user_data.find_one({"_id": ctx.author.id})
    user_inventory = list(user_data["inventory"])

    if item_index > len(user_inventory):
        await msg_embed(ctx, f"No item exists at index {item_index}")
        return

    #callbacks
    is_msg_deleted = False
    async def close_message():
        nonlocal is_msg_deleted
        if not is_msg_deleted:
            is_msg_deleted =True
            await msg.delete()

    async def sell_callback(interact: discord.Interaction):
        if interact.user.id == ctx.author.id:
            update_result = database.user_data.update_one(
                {"_id": ctx.author.id, "inventory": {"name": item, "float": float}},
                {
                    "$pull": {"inventory": {"name": item, "float": float}},
                    "$inc": {
                        "balance": database.skin_data[item]["price"],
                        "inventory-size": -1
                    }
                },
            )
            
            if update_result.matched_count == 0:
                await close_message()
                await msg_embed(ctx, f"Sell cancelled as the specific **{formatted_name}** is no longer in your inventory")
            else:
                await msg_embed_edit(msg, f"Successfully sold **{formatted_name}**", view=None)
        else:
            await interact.response.defer()

    async def cancel_callback(interact: discord.Interaction):
        if interact.user.id == ctx.author.id:
            await close_message()
        else:
            await interact.response.defer()

    item_index -= 1

    item = user_inventory[item_index]["name"]
    float = user_inventory[item_index]["float"]
    item_data = database.skin_data[item]
    formatted_name = item_data["formatted_name"]
    price = currency_str_format(item_data["price"])

    view = discord.ui.View(timeout=30)
    view.on_timeout = close_message
    confirm_button = discord.ui.Button(label="Yes", style=discord.ButtonStyle.green)
    confirm_button.callback = sell_callback

    cancel_button = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.red)
    cancel_button.callback = cancel_callback

    view.add_item(confirm_button)
    view.add_item(cancel_button)

    msg = await msg_embed(ctx, f"Are you sure you want to sell **{formatted_name}** for **{price}**?", view=view)