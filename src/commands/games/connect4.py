import discord
from discord.ext.commands import Context

async def connect4(ctx:Context, column:int):

    grid = [[":black_circle:" for col in range(7)] for row in range(6)]

    description = ""
    for row in range(6):
        for column in range(7):
            description += grid[row][column]
        description += "\n"

    e = discord.Embed(
        title="Connect 4!", 
        description=description)

    await ctx.send(embed=e)