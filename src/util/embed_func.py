import discord
from discord.ext.commands import Context

async def msg_embed(ctx:Context, msg:str):
    return await ctx.send(embed=discord.Embed(description=msg, color=discord.Color.dark_theme()))
