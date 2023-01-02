import discord
from src.util import database
from src.util.constants import PREFIX
from discord.ext.commands import Context
from datetime import datetime
from src.util.decorators import requires

@requires(users_registered=True)
async def send_trade_notif_to_user(sender: discord.Member, recipient:discord.Member):
    trade = database.trade_requests.find_one({"_id": sender.id, "recipient-id": recipient.id})

    e = discord.Embed(
        title=f"{sender.name} has sent you a trade request!",
        color=discord.Color.dark_theme()
    )
    e.set_thumbnail(url=sender.display_avatar.url)

    they_offer = create_item_str(trade["sender-items"])
    for_your = create_item_str(trade["recipient-items"])

    e.add_field(name="They Offer", value=they_offer)
    e.add_field(name="For Your", value=for_your)
    e.add_field(
        name="Commands", 
        value=f"""`{PREFIX}trade accept {sender.name}` - accept trade
        `{PREFIX}trade decline {sender.name}` - decline trade
        """,
        inline=False
    )
    await recipient.send(embed=e)
    

def create_item_str(items:list) -> str:
    if len(items) == 0:
        return "None"
    else:
        string = ""
        for count, item in enumerate(items):
            item_data = database.skin_data[item["name"]]
            string += f"**{count+1})** `{item_data['formatted_name']}`\n"
        return string

async def send_trade_embed(ctx:Context, trade:dict, incoming:bool):
    if incoming:
        user:discord.Member = await ctx.bot.fetch_user(trade["_id"])
        title = f"Incoming trade from {user.name}"
    else:
        user:discord.Member = await ctx.bot.fetch_user(trade["recipient-id"])
        title = f"Outgoing trade to {user.name}"

    e = discord.Embed(title=title, color=discord.Color.dark_theme())
    e.set_thumbnail(url=user.avatar.url)

    if incoming:
        your_items = create_item_str(trade["recipient-items"])      
        their_items = create_item_str(trade["sender-items"])
    else:
        your_items = create_item_str(trade["sender-items"])      
        their_items = create_item_str(trade["recipient-items"])

    e.add_field(name="They Want", value=your_items)
    e.add_field(name="For Their", value=their_items)

    if not incoming:
        e.add_field(name="Commands", inline=False, 
        value=f"""`{PREFIX}trade cancel {user.name}` - cancel trade
        """)

    timestamp = datetime.fromtimestamp(trade["send-timestamp"])
    datetime_str = timestamp.strftime("Trade created on %Y/%m/%d at %H:%M:%S")

    e.set_footer(icon_url=ctx.author.display_avatar.url, text=datetime_str)

    await ctx.send(embed=e)

async def send_trade_in_creation_embed(ctx:Context, recipient:discord.Member, trade:dict=None, confirmed:bool=False):
    if confirmed:
        title = f"Sent trade request to {recipient.name}"
    else:
        title = f"Trade request to {recipient.name}"
        
    e = discord.Embed(title=title)
    e.set_thumbnail(url=recipient.display_avatar.url)

    if confirmed:
        e.color = discord.Color.green()

    if trade is None:
        trade = database.trade_requests.find_one({"_id": ctx.author.id, "send-timestamp": 0})

        if trade is None:
            await ctx.send(f"You have no trade in creation! Use `{PREFIX}trade new <user>` to start a new trade")
            return

    your_items = create_item_str(trade["sender-items"])      
    their_items = create_item_str(trade["recipient-items"])

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