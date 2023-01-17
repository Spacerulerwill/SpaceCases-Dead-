import discord
import asyncio
from discord.ext.commands import Context
from src.util import database
from src.util.constants import MAX_TRADES_PER_PAGE
from src.util.constants import PREFIX
from src.util.embed_func import msg_embed
from src.util.decorators import requires

@requires(users_registered=True)
async def trades(ctx:Context, in_out:str, page:int):

    if in_out is None:
        in_out = "all"
    if page is None:
        page = 1
    elif page < 1:
        await msg_embed(ctx, "Invalid page number!")
        return
    
    if in_out == "all":
        title = "All Trade Requests"
        trades = list(database.trade_requests.find({"$or": [{"_id": ctx.author.id, "send-timestamp": {"$ne": 0}}, {"recipient-id": ctx.author.id, "send-timestamp": {"$ne": 0}}]}))
    elif in_out == "in":
        title = "Incoming Trade Requests"
        trades = list(database.trade_requests.find({"recipient-id": ctx.author.id, "send-timestamp": {"$ne": 0}}))
    elif in_out == "out":
        title = "Outgoing Trade Requests"
        trades = list(database.trade_requests.find({"_id": ctx.author.id, "send-timestamp": {"$ne": 0}}))

    trades_pages = [trades[x:x+MAX_TRADES_PER_PAGE] for x in range(0, len(trades), MAX_TRADES_PER_PAGE)]
    
    if len(trades) == 0:
        num_pages = 1
        page = 0
    else:
        num_pages = len(trades_pages)
        page -= 1
    
    async def get_trades_embed() -> discord.Embed:
        nonlocal num_pages, page

        if len(trades) == 0:
            trade_list_str = "None"
        else:

            try:
                current_trade_page = trades_pages[page]
            except IndexError:
                await msg_embed(ctx, "Invalid page number!")
                return
            
            trade_list_str = ""

            id_name_dict = {}
            async def get_name(_id: int):
                nonlocal id_name_dict
                user = ctx.guild.get_member(_id)
                
                if user is None:
                    user = await ctx.bot.fetch_user(_id)

                id_name_dict[_id] = user.name
            
            if in_out == "all":

                async with asyncio.TaskGroup() as tg:
                    for trade in current_trade_page:
                        if trade["_id"] == ctx.author.id:
                            tg.create_task(get_name(trade["recipient-id"]))
                        elif trade["recipient-id"] == ctx.author.id:
                            tg.create_task(get_name(trade["_id"]))


                for trade in current_trade_page:
                    if trade["_id"] == ctx.author.id:
                        recipient = id_name_dict[trade["recipient-id"]]
                        trade_list_str += f"**OUTGOING** to {recipient}\n"
                    elif trade["recipient-id"] == ctx.author.id:
                        sender = id_name_dict[trade["_id"]]
                        trade_list_str += f"**INCOMING** from {sender}\n"

            elif in_out == "in":

                async with asyncio.TaskGroup() as tg:
                    for trade in current_trade_page:
                        tg.create_task(get_name(trade["_id"]))

                for trade in current_trade_page:
                    sender = id_name_dict[trade["_id"]]
                    trade_list_str += f"**INCOMING** from {sender}\n"

            elif in_out == "out":

                async with asyncio.TaskGroup() as tg:
                    for trade in current_trade_page:
                        tg.create_task(get_name(trade["recipient-id"]))

                for trade in current_trade_page:
                    recipient = id_name_dict[trade["recipient-id"]]
                    trade_list_str += f"**OUTGOING** to {recipient}\n"

        e = discord.Embed(title=title, color=discord.Color.dark_theme())
        e.set_thumbnail(url=ctx.author.display_avatar.url)
        e.add_field(name=f"Trade List - {len(trades)} Items - Page {page+1}/{num_pages}", value=trade_list_str)
        e.add_field(name="Commands", 
        value=f"""`{PREFIX}trade in <user>` - view incoming trade from user
        `{PREFIX}trade out <user>` - view outgoing trade to user
        `{PREFIX}trade accept <user>` - accept trade from user
        `{PREFIX}trade decline <user>` - decline trade from user
        `{PREFIX}trade cancel <user>` - cancel trade to user
        """,
        inline=False)
        
        return e

    # if more than one page, create view
    async def next_callback(interact:discord.Interaction):
        nonlocal page

        if page < num_pages - 1:
            page += 1
        else:
            page = 0

        await interact.response.edit_message(embed=await get_trades_embed())

    async def prev_callback(interact:discord.Interaction):
        nonlocal page

        if page > 0:
            page -= 1
        else:
            page = num_pages - 1

        await interact.response.edit_message(embed=await get_trades_embed())

    async def view_timeout_callback():
        await msg.delete()

    view = None
    if num_pages > 1:
        view = discord.ui.View()
        view.on_timeout = view_timeout_callback
        prev_button = discord.ui.Button(label="◀", style=discord.ButtonStyle.gray)
        prev_button.callback = prev_callback
        next_button = discord.ui.Button(label="▶", style=discord.ButtonStyle.gray)
        next_button.callback = next_callback
        view.add_item(prev_button)
        view.add_item(next_button)

    msg = await ctx.send(embed=await get_trades_embed(), view=view)