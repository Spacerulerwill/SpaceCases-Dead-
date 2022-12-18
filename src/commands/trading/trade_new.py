import discord
from discord.ext.commands import Context
from src.util import database
from src.util.constants import PREFIX
from src.commands.trading.trade import send_trade_embed

from typing import Tuple

async def send_warning(ctx:Context, recipient:discord.Member):
    e = discord.Embed(
        title="Warning: You already have a trade request in creation",
        description="This trade request will be deleted. Continue?",
        color=discord.Color.red()
    )
    e.set_thumbnail(url=ctx.author.avatar.url)
    e.set_footer(text="Trade request creation will automatically cancel after 30 seconds of inactivity")

    # callback funcs
    async def view_timeout_callback():
        await close_message()

    async def close_message():
        try:
            await msg.delete()
        except discord.errors.NotFound:
            pass

    async def cancel_callback(interact: discord.Interaction):
        await close_message()
        await interact.response.defer()

    async def continue_callback(interact: discord.Interaction):
        trade =  {
            "_id": ctx.author.id,
            "send-timestamp": 0,
            "recipient-id": recipient.id,
            "sender-items": [],
            "recipient-items": [],
            "send-timestamp": 0
        }
        database.trade_requests.update_one(
            {"_id": ctx.author.id, "send-timestamp": 0},
            {
                "$set": trade
            },
            upsert=True
        )
        
        await close_message()
        await send_trade_embed(ctx, recipient, trade)  

    view = discord.ui.View(timeout=30)
    view.on_timeout = view_timeout_callback

    continue_button = discord.ui.Button(label="Continue", style=discord.ButtonStyle.green)
    continue_button.callback = continue_callback
    cancel_button = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.red)
    cancel_button.callback = cancel_callback
    view.add_item(continue_button)
    view.add_item(cancel_button)

    msg = await ctx.send(embed=e, view=view)

def try_create_trade_request(ctx:Context, recipient:discord.Member) -> Tuple[bool, dict]:
    trade = {
        "_id": ctx.author.id,
        "recipient-id": recipient.id,
        "sender-items": [],
        "recipient-items": [],
        "send-timestamp": 0
    }
    update_result = database.trade_requests.update_one(
        {"_id": ctx.author.id, "send-timestamp": 0},
        {
            "$setOnInsert": trade
        },
        upsert=True
    )

    return update_result.upserted_id is not None, trade

async def new(ctx:Context, recipient:discord.Member):
    if database.user_data.find_one({"_id": ctx.author.id}) is None:
        await ctx.send(f"You are not registered! Use `{PREFIX}register` to register")
        return
    
    if database.user_data.find_one({"_id": recipient.id}) is None:
        await ctx.send(f"{recipient.name} is not registered!")
        return
    
    successful, trade = try_create_trade_request(ctx, recipient)
    
    if successful:
        # create new trade and show trade embed
        await send_trade_embed(ctx, recipient, trade)
    else:
        # show warning that this will override previous trade
        await send_warning(ctx, recipient)
