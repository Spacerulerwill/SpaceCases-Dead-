import discord
from discord.ext.commands import Context
from src.util import database
from src.util.format import currency_str_format

async def balance(ctx: Context, member: discord.Member = None):
        if member is None:
            member = ctx.author

        user_data:dict = database.user_data.find_one({"_id": member.id})

        if user_data is not None: 
            await ctx.send(f"{member.name}'s balance is: {currency_str_format(user_data['balance'])}")
        else:
            await ctx.send(f"{member.name} is not registered!")