"""
Copyright (C) 2023 William Redding - All Rights Reserved

Commands
~~~~~~~~
* leaderboard
* ranking

See end of file for licence details
"""

import discord
from discord.ext import commands
from discord.ext.commands import Context
from discord.ext.commands.bot import Bot

from typing import Literal, Optional

# command imports
from src.commands.rankings.leaderboard import leaderboard
from src.commands.rankings.ranking import ranking


# initialise class
class Rankings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def leaderboard(
        self,
        ctx: Context,
        global_local: Optional[Literal["global", "local"]] = "global",
        page: Optional[int] = 1,
    ):
        await leaderboard(ctx, global_local, page)

    @commands.command()
    async def ranking(
        self,
        ctx: Context,
        global_local: Optional[Literal["global", "local"]] = "global",
        user: Optional[discord.Member] = None,
    ):
        await ranking(ctx, global_local, user)


# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot: Bot):
    await bot.add_cog(Rankings(bot))


"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
