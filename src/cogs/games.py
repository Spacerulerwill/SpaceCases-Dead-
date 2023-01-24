"""
Games Command Cog
~~~~~~~~~~~~~~~~~~~

This cog contains the commands:
* skin?
* coinflip
"""

from discord.ext import commands
from discord.ext.commands import Context
from src.util.constants import PREFIX
from src.util.string_util import currency_str_format

from typing import Literal
from decimal import Decimal

# commands
from src.commands.games.skin_game import skin_game, SKIN_GAME_PRICE, SKIN_GAME_REWARD
from src.commands.games.coinflip import coinflip
from src.commands.games.higher_lower import higher_lower

# initialise class
class Games(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @commands.command(name="skin?", description="Play the skin guessing game!", usage=
    {
        "Syntax": f"`{PREFIX}skin?`",
        "How To Play": f"""Use the command and reply to the message with the name of the skin **within 10 seconds!** Do **not** include the condition or the name of the weapon, just the skin name. 
        
        It costs **{currency_str_format(SKIN_GAME_PRICE)}** to play, winning rewards you with **{currency_str_format(SKIN_GAME_REWARD)}!**"""
    })
    async def skin_game(self, ctx:Context):
        await skin_game(ctx)

    @commands.command(description="Bet money and flip a coin!", usage={
        "Syntax": f"`{PREFIX}coinflip <t/ct> <amount>`",
        "Arguments": """
        `<t/ct>` - whether to bet on the coin landing on the t or ct side
        `<amount>` - the amount of money to bet on the coin flip
        """,
        "How To Play": "Use the command to bet an amount on the coinflip. If you guess correctly, your money will be doubled. But if you get it wrong, you will lose it."
    }, aliases=["flip", "coin"])
    async def coinflip(self, ctx:Context, t_ct:Literal["t", "ct"], amount:Decimal):
        await coinflip(ctx, t_ct, amount)

    @commands.command(description="Play the higher or lower game!", usage={
        "Syntax": f"`{PREFIX}hl <difficulty>`",
        "Arguments": "`<difficulty>` - the amount of correct guessed needed before receiving prize",
        "How To Play": "Try and figure out if the price of the skin is more or less expensive than the previous one! Choose a difficulty from 3 to 10, which dictates the amount of correct guessed needed before winning"
    })
    async def hl(self, ctx:Context, difficulty:int=3):
        await higher_lower(ctx, difficulty)

# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(Games(bot))