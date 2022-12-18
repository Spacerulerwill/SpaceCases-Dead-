import discord
from src.util import database
from src.util.constants import PREFIX
from discord.ext.commands import Context

async def send_trade_embed(ctx:Context, recipient:discord.Member, trade:dict):
    e = discord.Embed(title=f"Trade request to {recipient.name}")
    e.set_thumbnail(url=recipient.avatar.url)

    if len(trade["sender-items"]) == 0:
        your_items = "None"
    
    if len(trade["recipient-items"]) == 0:
        their_items = "None"

    e.add_field(name="Your Items", value=your_items)
    e.add_field(name="Their Items", value=their_items)

    e.add_field(
        name="Commands", 
        value=f"""`{PREFIX}trade cancel`
        `{PREFIX}trade add in/out <item number>`
        `{PREFIX}trade add in/out <item number>`
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