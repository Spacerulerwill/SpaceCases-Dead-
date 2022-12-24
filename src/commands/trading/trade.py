import discord
from src.util import database
from src.util.constants import PREFIX
from discord.ext.commands import Context

async def send_trade_embed(ctx:Context, recipient:discord.Member, trade:dict=None, confirmed:bool=False):

    if confirmed:
        title = f"Sent trade request to {recipient.name}"
    else:
        title = f"Trade request to {recipient.name}"
        
    e = discord.Embed(title=title)
    e.set_thumbnail(url=recipient.avatar.url)

    if confirmed:
        e.color = discord.Color.green()

    if trade is None:
        trade = database.trade_requests.find_one({"_id": ctx.author.id, "send-timestamp": 0})

    if trade is None:
        await ctx.send(f"You have no trade in creation! Use `{PREFIX}trade new <user>` to start a new trade")
        return

    if len(trade["sender-items"]) == 0:
        your_items = "None"
    else:
        your_items = ""
        for count, item in enumerate(trade["sender-items"]):
            item_data = database.skin_data[item["name"]]
            your_items += f"**{count+1})** `{item_data['formatted_name']}`\n"
            
    if len(trade["recipient-items"]) == 0:
        their_items = "None"
    else:
        their_items = ""
        for count, item in enumerate(trade["recipient-items"]):
            item_data = database.skin_data[item["name"]]
            their_items += f"**{count+1})** `{item_data['formatted_name']}`\n"

    e.add_field(name="Your Items", value=your_items)
    e.add_field(name="Their Items", value=their_items)

    if not confirmed:
        e.add_field(
            name="Commands", 
            value=f"""`{PREFIX}trade cancel` - cancel trade
            `{PREFIX}trade add in/out <inventory item number>` - add item
            `{PREFIX}trade remove in/out <trade item number>` - remove item
            `{PREFIX}trade send` - send trade 
            """, 
            inline=False
        )

    await ctx.send(embed=e)

async def view_trade_in_creation(ctx:Context):
    trade = database.trade_requests.find_one({"_id": ctx.author.id, "send-timestamp":0})
    if trade is None:
        await ctx.send(f"You have no trade in creation! Use `{PREFIX}trade new <user>` to start a new trade")
        return

    recipient = await ctx.bot.fetch_user(trade["recipient-id"])
    await send_trade_embed(ctx, recipient, trade)