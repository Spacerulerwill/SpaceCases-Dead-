import discord
from discord.ext.commands import Context
from src.util import database
from src.util.string_util import currency_str_format

async def balance(ctx: Context, member: discord.Member = None):
    if member is None:
        member = ctx.author

    user_data:dict = database.user_data.find_one({"_id": member.id})

    if user_data is not None: 
        e = discord.Embed(title=f"{member.name}'s Balance", color=discord.Color.dark_theme())
        e.set_thumbnail(url=member.display_avatar.url)
        e.add_field(name="Current Balance", value=currency_str_format(user_data["balance"]))
        e.add_field(name="Total Earned", value="$0.00")
        e.add_field(name="Total Spent", value="$0.00")
        await ctx.send(embed=e)
    else:
        await ctx.send(f"{member.name} is not registered!")