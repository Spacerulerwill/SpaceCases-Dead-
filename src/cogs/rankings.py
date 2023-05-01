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

# commands
from src.commands.rankings.leaderboard import leaderboard
from src.commands.rankings.ranking import ranking

from typing import Literal, Optional

# initialise class
class Rankings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def leaderboard(self, ctx: Context, global_local:Optional[Literal["global", "local"]]="global", page: Optional[int] = 1):
        await leaderboard(ctx, global_local, page)

    @commands.command()
    async def ranking(self, ctx: Context, global_local:Optional[Literal["global", "local"]]="global", user: Optional[discord.Member] = None):
        await ranking(ctx, global_local, user)


# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(Rankings(bot))
