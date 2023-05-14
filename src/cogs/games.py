"""
Copyright (C) 2023 William Redding - All Rights Reserved

Commands
~~~~~~~~
* skin?
* coinflip
* wordle
* hl
* ttt

See end of file for licence details
"""

import discord
from discord.ext import commands
from discord.ext.commands import Context
from discord.ext.commands.bot import Bot
from src.util.constants import HL_MIN_GUESS

from typing import Literal
from decimal import Decimal

# command imports
from src.commands.games.skin_game import skin_game
from src.commands.games.coinflip import coinflip
from src.commands.games.higher_lower import higher_lower
from src.commands.games.wordle import wordle
from src.commands.games.ttt import ttt


# initialise class
class Games(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def skin_game(self, ctx: Context):
        await skin_game(ctx)

    @commands.command()
    async def coinflip(self, ctx: Context, side: Literal["t", "ct"], amount: Decimal):
        await coinflip(ctx, side, amount)

    @commands.command()
    async def hl(self, ctx: Context, difficulty: int = HL_MIN_GUESS):
        await higher_lower(ctx, difficulty)

    @commands.command()
    async def wordle(self, ctx: Context, guess: str = None):
        await wordle(ctx, guess)

    @commands.command()
    async def ttt(self, ctx: Context, player2: discord.Member, bet: Decimal = 0):
        await ttt(ctx, player2, bet)


# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot: Bot):
    await bot.add_cog(Games(bot))


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
