import discord
from src.util import database
from discord.ext.commands import Context
from src.commands.trading.trade_func import create_item_str

async def decline(ctx:Context, sender:discord.Member):
    deleted_document = database.trade_requests.find_one_and_delete({"_id": sender.id, "recipient-id": ctx.author.id, "send-timestamp": {"$ne": 0}})
    
    if deleted_document is None:
        await ctx.send(f"You do not have an incoming trade from {sender.name}!")
    else:
        #inform recipient trade has been declined
        e = discord.Embed(title=f"Trade request from {sender.name} declined", color=discord.Color.red())
        
        await ctx.send(embed=e)

        #inform original sender that their request was declined
        e = discord.Embed(title=f"Your trade request to {ctx.author.name} was declined", color=discord.Color.red())
        e.set_thumbnail(url=sender.default_avatar.url)

        you_wanted = create_item_str(deleted_document["recipient-items"])
        for_your = create_item_str(deleted_document["sender-items"])
        e.add_field(name="You Wanted", value=you_wanted)
        e.add_field(name="For Your", value=for_your)
        await sender.send(embed=e)

