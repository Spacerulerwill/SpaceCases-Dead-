import discord
from src.util import database
from src.util.constants import PREFIX
from discord.ext.commands import Context

# send the embed and view for the user creating the trade
async def send_trade_embed_view(ctx: Context, sender:discord.Member, recipient:discord.Member) -> discord.Embed:

    trade = database.user_trade_creation[sender.id]

    def get_embed():
        e = discord.Embed(title=f"Trade request to {recipient.name}", description=steps[trade["step"]])
        e.set_thumbnail(url=recipient.avatar.url)

        if len(trade["sender_items"]) == 0:
            your_items = "None"
        else:
            your_items = ""
            for count, item in enumerate(trade["sender_items"]):
                name = item["name"]
                your_items += f"**{count+1})** {database.skin_data[name]['formatted_name']}\n"
        
        if len(trade["recipient_items"]) == 0:
            their_items = "None"
        else:
            their_items = ""
            for count, item in enumerate(trade["recipient_items"]):
                name = item["name"]
                their_items += f"**{count+1})** {database.skin_data[name]['formatted_name']}\n"

        e.add_field(name="Your Items", value=your_items)
        e.add_field(name="Their Items", value=their_items)
        e.add_field(name="Commands", value=f"`{PREFIX}trade add <inventory index>`\n`{PREFIX}trade remove <item number>`", inline=False)
        e.set_footer(icon_url=sender.avatar.url, text="Warning! Trade will cancel after 10 minutes of inactivity")

        return e
    
    def get_view():
        view = discord.ui.View(timeout=600)
        cancel_button = discord.ui.Button(style=discord.ButtonStyle.red, label="Cancel")
        cancel_button.callback = cancel_callback
        if trade["step"] == 3:
            next_button = discord.ui.Button(style=discord.ButtonStyle.green, label="Send Trade")
        else:
            next_button = discord.ui.Button(style=discord.ButtonStyle.gray, label="Next Step")
        next_button.callback = next_callback
        view.on_timeout = view_timeout_callback
        view.add_item(next_button)
        view.add_item(cancel_button)

        return view

    async def view_timeout_callback():
        await msg.delete()
        del database.user_trade_creation[sender.id]

    #callbacks
    async def cancel_callback(interact:discord.Interaction):
        if interact.user.id == sender.id and msg.id == trade["msg"].id:
            await msg.delete()
            del database.user_trade_creation[sender.id]
        await interact.response.defer()
    
    async def next_callback(interact:discord.Interaction):
        if interact.user.id == sender.id and msg.id == trade["msg"].id:
            if trade["step"] != 3:
                # go to next step
                trade["step"] += 1
                await msg.edit(embed=get_embed(), view=get_view())
            else:
                #submit trade
                e = discord.Embed(
                    color=discord.Color.green(), 
                    title=f"Trade request to {recipient.name} sent!",
                    description="They have 7 days to accept your request"
                )
                e.set_thumbnail(url=recipient.avatar.url)
                await msg.edit(embed=e, view=None)
                del database.user_trade_creation[sender.id]

        await interact.response.defer()

    if trade["msg"] is None:
        msg = await ctx.send(embed=get_embed(), view=get_view())
        trade["msg"] = msg
    else:
        msg = await ctx.send(embed=get_embed(), view=get_view())
        trade["msg"] = msg


steps = {
    1: f"**Step 1:** Choose items to **give**",
    2: f"**Step 2:** Choose items to **recieve**",
    3: f"**Step 3:** Review and confirm your trade"
}

async def trade(ctx:Context, member:discord.Member):
    if database.user_data.find_one({"_id": ctx.author.id}) == None:
        await ctx.send(f"You are not registered! Use `{PREFIX}register` to register")
        return

    if database.user_data.find_one({"_id": member.id}) == None:
        await ctx.send(f"{member.name} is not registered!")
        return

    if ctx.author.id is member.id:
        await ctx.send("You cannot trade items to yourself!")
        return

    #if user is already in the middle of creating a trade
    if database.user_trade_creation.get(ctx.author.id) != None:
        e = discord.Embed(
            title="Warning! Trade already in creation", 
            description="Creating a new trade will delete the current one! Are you sure you want to continue?", 
            color=discord.Color.red()
        )
        e.set_thumbnail(url=ctx.author.avatar.url)

        await ctx.send(embed=e)
        return
    
    database.user_trade_creation[ctx.author.id] = {"msg": None, "recipient": member.id, "sender_items": [], "recipient_items": [], "step": 1}
    await send_trade_embed_view(ctx, ctx.author, member)