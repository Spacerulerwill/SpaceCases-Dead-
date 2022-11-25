import discord
from discord.ext.commands import Context
from src.util.constants import PREFIX
from src.util import database

async def inventory(ctx:Context, member:discord.Member, page:int):

    if member == None:
        member = ctx.author
    
    user_data = database.user_data.find_one({"_id":member.id})

    # if user doesn't exist
    if user_data == None:
        if member == ctx.author:
            await ctx.send(f"You are not registered! Use `{PREFIX}register` to register")
        else:
            await ctx.send(f"{member.name} is not registered!")
        return
    
    e = discord.Embed(title=f"{member.name}'s Inventory")

    # if users inventory is empty
    if user_data["item-count"] == 0:
        if member == ctx.author:
            e.description = f"Your inventory is empty! Start unboxing with `{PREFIX}open`"
        else:
            e.description = f"{member.name}'s inventory is empty!"
        await ctx.send(embed=e)
        return