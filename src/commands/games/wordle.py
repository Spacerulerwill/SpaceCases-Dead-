import discord
import random
from discord.ext.commands import Context
from src.util import database

ANSI_GREEN = "\u001b[0;32m"
ANSI_RED = "\u001b[0;33m"
ANSI_GRAY = "\u001b[0;30m"
CLEAR = "\u001b[0m"

async def wordle(ctx:Context):
    guesses = 5

    random_word = random.choice(database.word_list)

    e = discord.Embed(color=discord.Color.dark_theme())
    e.description = f"""
    **Guesses:** {guesses}
    **Streak:** 1
    """ + f"```ansi\n{ANSI_GREEN}{random_word.upper()}{CLEAR}\n{ANSI_GRAY}XXXXX\nXXXXX\nXXXXX\nXXXXX\nXXXXX```" 

    view = discord.ui.View(timeout=300)
    guess_button = discord.ui.Button(label="Guess!", style=discord.ButtonStyle.green)

    view.add_item(guess_button)

    await ctx.send(embed=e, view=view)