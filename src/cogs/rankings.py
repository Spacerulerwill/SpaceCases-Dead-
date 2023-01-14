"""
Rankings Command Cog
~~~~~~~~~~~~~~~~~~~

This cog contains the commands:
* leaderboard
* ranking
"""

import discord
from discord.ext import commands
from discord.ext.commands import Context
from src.util.constants import PREFIX

#commands
from src.commands.rankings.leaderboard import leaderboard
from src.commands.rankings.ranking import ranking

# initialise class
class Rankings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="View a page on the leaderboard", usage={
        "Syntax": f"`{PREFIX}leaderboard <page number>`",
        "Arguments": "`<page number>` - the page of the leaderboard - optional"
    })
    async def leaderboard(self, ctx:Context, page:int=1):
        await leaderboard(ctx, page)

    @commands.command(description="View your position on the leaderboard", usage={
        "Syntax": f"`{PREFIX}ranking <user>`",
        "Arguments": "`<user>` - user to check ranking of - optional"
    })
    async def ranking(self, ctx:Context, user:discord.Member=None):
        await ranking(ctx, user)

# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(Rankings(bot))