"""
Games Command Cog
~~~~~~~~~~~~~~~~~~~

This cog contains the commands:
* skin?
* coinflip
* hl 
* wordle
* connect4
* ttt
"""

import discord
from discord.ext import commands
from discord.ext.commands import Context
from src.util.constants import PREFIX
from src.util.string_util import currency_str_format

from typing import Literal
from decimal import Decimal

# commands
from src.commands.games.skin_game import skin_game, SKIN_GAME_PRICE, SKIN_GAME_REWARD
from src.commands.games.coinflip import coinflip
from src.commands.games.higher_lower import (
    higher_lower,
    HL_MIN_GUESS,
    HL_MAX_GUESS,
    HL_PRICE,
)
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
async def setup(bot):
    await bot.add_cog(Games(bot))
