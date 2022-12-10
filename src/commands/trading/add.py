import discord
from src.util import database
from src.util.constants import PREFIX
from discord.ext.commands import Context
from pymongo import ReturnDocument

async def add(ctx:Context, item_index:int):
    try:
        user_trade = database.user_trade_creation[ctx.author.id]
        sender_inventory = database.user_data.find_one_and_update({"_id": ctx.author.id}, {
           "$set": {
                f"inventory.{item_index-1}.trade_locked": True
           }
        }, return_document=ReturnDocument.AFTER)["inventory"]
        user_trade["sender_items"].append(sender_inventory[item_index-1])

        user = await ctx.bot.fetch_user(user_trade["recipient"])
        e = discord.Embed(title=f"Trade request to {user.name}")
        e.set_thumbnail(url=user.avatar.url)

        sender_items_str = ""
        for count, item in enumerate(user_trade["sender_items"]):
            item_data = database.skin_data[item["name"]]
            sender_items_str += f"**{count+1})** {item_data['formatted_name']}\n"
            
        e.add_field(name="Your Items", value=sender_items_str)
        e.add_field(name="Their Items", value="None")

        await ctx.send(embed=e)

    except KeyError:
        pass
