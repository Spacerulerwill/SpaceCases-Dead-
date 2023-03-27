import discord
import asyncio
from datetime import datetime, timedelta
from discord.ext.commands import Context
from src.util import database
from src.util.lang import get_locale
from src.util.constants import MAX_TRADES_PER_PAGE
from src.util.constants import PREFIX
from src.util.embed_func import msg_embed, msg_embed_response
from src.util.decorators import requires

@requires(users_registered=True)
async def trades(ctx:Context, in_out:str, page:int):
    lang = database.user_data.find_one({"_id": ctx.author.id})["language"]

    if in_out is None:
        in_out = "all"
    if page is None:
        page = 1
    elif page < 1:
        await msg_embed(ctx, get_locale(lang, "invalid_page"))
        return
    
    if in_out == "all":
        title = get_locale(lang, "trades.all.embed.title")
        trades = list(database.trade_requests.find({"$or": [{"_id": ctx.author.id, "send-timestamp": {"$ne": 0}}, {"recipient-id": ctx.author.id, "send-timestamp": {"$ne": 0}}]}))
    elif in_out == "in":
        title = get_locale(lang, "trades.in.embed.title")
        trades = list(database.trade_requests.find({"recipient-id": ctx.author.id, "send-timestamp": {"$ne": 0}}))
    elif in_out == "out":
        title = get_locale(lang, "trades.out.embed.title")
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
            trade_list_str = get_locale(lang, "none")
        else:

            try:
                current_trade_page = trades_pages[page]
            except IndexError:
                await msg_embed(ctx, get_locale(lang, "invalid_page"))
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
                    time_left:timedelta = (trade["send-timestamp"] + one_week) - now
                    
                    if trade["_id"] == ctx.author.id:
                        recipient = id_name_dict[trade["recipient-id"]]
                        trade_list_str += get_locale(lang, "trades.outgoing_to", recipient, time_left.days)
                    elif trade["recipient-id"] == ctx.author.id:
                        sender = id_name_dict[trade["_id"]]
                        trade_list_str += get_locale(lang, "trades.incoming_from", sender, time_left.days)

            elif in_out == "in":

                async with asyncio.TaskGroup() as tg:
                    for trade in current_trade_page:
                        tg.create_task(get_name(trade["_id"]))

                for trade in current_trade_page:
                    time_left:timedelta = (trade["send-timestamp"] + one_week) - now
                    sender = id_name_dict[trade["_id"]]
                    trade_list_str += get_locale(lang, "trades.incoming_from", sender, time_left.days)

            elif in_out == "out":

                async with asyncio.TaskGroup() as tg:
                    for trade in current_trade_page:
                        tg.create_task(get_name(trade["recipient-id"]))

                for trade in current_trade_page:
                    time_left:timedelta = (trade["send-timestamp"] + one_week) - now
                    recipient = id_name_dict[trade["recipient-id"]]
                    trade_list_str += get_locale(lang, "trades.outgoing_to", recipient, time_left.days)

        e = discord.Embed(title=title, color=discord.Color.dark_theme())
        e.set_thumbnail(url=ctx.author.display_avatar.url)
        e.add_field(name=get_locale(lang, "trades.embed.trade_list", len(trades), page+1, num_pages), value=trade_list_str)
        e.add_field(name="Commands", value=get_locale(lang, "trades.embed.commands.value", PREFIX, PREFIX, PREFIX, PREFIX, PREFIX), inline=False)
        
        return e

    # if more than one page, create view
    async def next_callback(interact:discord.Interaction):

        if interact.user.id != ctx.author.id:
            await msg_embed_response(interact.response, get_locale(lang, "not_your_button"), ephemeral=True)
            return

        nonlocal page

        if page < num_pages - 1:
            page += 1
        else:
            page = 0

        await interact.response.edit_message(embed=await get_trades_embed())

    async def prev_callback(interact:discord.Interaction):
        if interact.user.id != ctx.author.id:
            await msg_embed_response(interact.response, get_locale(lang, "not_your_button"), ephemeral=True)
            return
            
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
    
    now = datetime.utcnow()
    one_week = timedelta(weeks=1)
    msg = await ctx.send(embed=await get_trades_embed(), view=view)