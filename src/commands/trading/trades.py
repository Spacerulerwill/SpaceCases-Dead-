import discord
from discord.ext.commands import Context
from src.util import database
from src.util.constants import PREFIX

async def trades(ctx:Context, in_out:str):
    if in_out == "all":
        title = "All Trade Requests"
        trades = list(database.trade_requests.find({"$or": [{"_id": ctx.author.id, "send-timestamp": {"$ne": 0}}, {"recipient-id": ctx.author.id, "send-timestamp": {"$ne": 0}}]}))
    elif in_out == "in":
        title = "Incoming Trade Requests"
        trades = list(database.trade_requests.find({"recipient-id": ctx.author.id, "send-timestamp": {"$ne": 0}}))
    elif in_out == "out":
        title = "Outgoing Trade Requests"
        trades = list(database.trade_requests.find({"_id": ctx.author.id, "send-timestamp": {"$ne": 0}}))

    if len(trades) == 0:
        trade_list_str = "None"
    else:
        trade_list_str = ""
        
        if in_out == "all":
            for trade in trades:
                if trade["_id"] == ctx.author.id:
                    recipient = await ctx.bot.fetch_user(trade["recipient-id"])
                    trade_list_str += f"**OUTGOING** to {recipient.name}\n"
                elif trade["recipient-id"] == ctx.author.id:
                    sender = await ctx.bot.fetch_user(trade["_id"])
                    trade_list_str += f"**INCOMING** from {sender.name}\n"
        elif in_out == "in":
            for trade in trades:
                sender = await ctx.bot.fetch_user(trade["_id"])
                trade_list_str += f"**INCOMING** from {sender.name}\n"
        elif in_out == "out":
            for trade in trades:
                recipient = await ctx.bot.fetch_user(trade["recipient-id"])
                trade_list_str += f"**OUTGOING** to {recipient.name}\n"

    e = discord.Embed(title=title, color=discord.Color.dark_theme())
    e.set_thumbnail(url=ctx.author.avatar.url)
    e.add_field(name=f"Trade List - {len(trades)} Items", value=trade_list_str)
    e.add_field(name="Commands", 
    value=f"""`{PREFIX}trade in <user>` - view incoming trade from user
    `{PREFIX}trade out <user>` - view outgoing trade to user
    `{PREFIX}trade accept <user>` - accept trade from user
    `{PREFIX}trade decline <user>` - decline trade from user
    `{PREFIX}trade cancel <user>` - cancel trade to user
    """,
    inline=False)

    await ctx.send(embed=e)