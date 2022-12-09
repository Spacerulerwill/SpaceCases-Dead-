import discord
from src.util import database
from src.util.constants import PREFIX
from discord.ext import commands
from discord.ext.commands import Context

async def trade(ctx:Context, bot: commands.Bot, member:discord.Member):
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

    database.user_trade_creation[ctx.author.id] = {"recipient": member.id, "sender_items": [], "recipient_items": []}
    e = discord.Embed(title=f"Trade request to {member.name}")
    e.set_thumbnail(url=member.avatar.url)
    e.add_field(name="Your Items", value="None")
    e.add_field(name="Their Items", value="None")

    async def cancel_callback(interact:discord.Interaction):
        if ctx.author.id == interact.user.id:
            del database.user_trade_creation[ctx.author.id]
            await msg.delete()

        await interact.response.defer()

    view = discord.ui.View()
    cancel_button = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.red)
    cancel_button.callback = cancel_callback
    view.add_item(cancel_button)

    msg = await ctx.send(embed=e, view=view) 
