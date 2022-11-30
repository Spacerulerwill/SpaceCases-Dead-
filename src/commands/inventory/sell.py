import discord
from src.util import database
from src.util.format import currency_str_format
from src.util.constants import PREFIX
from discord.ext.commands import Context

async def sell(ctx:Context, item_index:int):
    user_data = database.user_data.find_one({"_id": ctx.author.id})

    if user_data is None:
        await ctx.send(f"You are not registered! Use `{PREFIX}register` to register")
        return
    
    user_inventory = list(user_data["inventory"])

    if item_index > len(user_inventory):
        await ctx.send(f"No item exists at index {item_index}")
        return

    #callbacks
    is_msg_deleted = False
    async def close_message():
        nonlocal is_msg_deleted
        if not is_msg_deleted:
            is_msg_deleted =True
            await msg.delete()

    async def sell_callback(interact: discord.Interaction):
 
        #start a session to multi docuemnt atomic transaction
        with database.mongo_client.start_session() as session:
            with session.start_transaction():
                update_result = database.user_data.update_one({
                    "_id": ctx.author.id}, 
                    {
                        "$pull": {"inventory": {"name": item, "float": float}},
                    }, 
                session=session)

                if update_result.modified_count == 0:
                    await close_message()
                    await ctx.send(f"Sell cancelled as the **{formatted_name}** is no longer in your inventory")
                    session.abort_transaction()
                    return
                
                database.user_data.update_one({
                    "_id": ctx.author.id}, 
                    {
                        "$inc": {"balance": database.skin_data[item]["price"]}
                    }, 
                session=session)

        await msg.edit(content=f"Successfully sold **{formatted_name}**", view=None)

    async def cancel_callback(interact: discord.Interaction):
        await close_message()

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

    msg = await ctx.send(f"Are you sure you want to sell **{formatted_name}** for **{price}**?", view=view)