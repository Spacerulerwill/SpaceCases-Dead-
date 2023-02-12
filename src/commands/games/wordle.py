import discord
import random
import collections
from discord.ext.commands import Context
from src.util.decorators import requires
from src.util.constants import PREFIX
from src.util.string_util import currency_str_format
from src.util.embed_func import msg_embed
from src.util import database
from src.util.emojis import green_letters, yellow_letters, gray_letters, BLANK_LETTER

BLANK_ROW = BLANK_LETTER * 5 + "\n"
guess_result_default = [None for x in range(5)]

WORLDE_PRICE = 250
WORLD_REWARD = lambda remaining_guesses: WORLDE_PRICE + 500 + (remaining_guesses * 250)

NOT_ENOUGH_FUNDS_MSG = f"You do not have enough funds for this action. You need **{currency_str_format(WORLDE_PRICE)}** to play!"

def get_wordle_embed(ctx:Context, game_data:dict, won:bool=False, lost:bool=False) -> discord.Embed:
    description = ""

    if won:
        title=f"You Won {currency_str_format(WORLD_REWARD(game_data['remaining-guesses']))}!"
        color = discord.Color.green()
    elif lost:
        title=f"You Lost!"
        description += f"The word was `{game_data['answer']}`\n"
        color = discord.Color.red()
    else:
        title=""
        color = discord.Color.dark_theme()

    for guess in game_data["guesses"]:
        description += guess + "\n"

    for i in range(game_data["remaining-guesses"]):
        description += BLANK_ROW

    e = discord.Embed(
        title=title,
        color=color,
        description=description
    )

    return e

async def new_game(ctx:Context) -> dict:
    # check user has enough to play
    update_result = database.user_data.update_one({"_id": ctx.author.id},
    [{
        "$set": {
            "balance": {
                "$cond": {
                    "if": {"$gte": ["$balance", WORLDE_PRICE]},
                    "then": {"$subtract": ["$balance", WORLDE_PRICE]},
                    "else": "$balance"
                }
            }
        }
    }])

    if update_result.modified_count == 0:
        await msg_embed(ctx, NOT_ENOUGH_FUNDS_MSG)
        return

    game_data = {
        "user-id": ctx.author.id,
        "answer": random.choice(database.word_list),
        "remaining-guesses": 6,
        "guesses": []
    }

    return game_data

@requires(users_registered=True)
async def wordle(ctx:Context, guess:str):

    # no guess - just see current game, or create new one if none is started
    if guess is None:
        try:
            game_data = database.wordle_games[ctx.author.id]
        except KeyError:
            game_data = await new_game(ctx)
            database.wordle_games[ctx.author.id] = game_data
    
        await ctx.send(embed=get_wordle_embed(ctx, game_data))
    else:
        # they made a guess - play the game
        try:
            await guess_word(ctx, guess)
        except KeyError:
            game_data = await new_game(ctx)
            database.wordle_games[ctx.author.id] = game_data
            await guess_word(ctx, guess)

# guess word logic
async def guess_word(ctx:Context, guess:str):
    game_data = database.wordle_games[ctx.author.id]
    answer = game_data["answer"]

    guess = guess.lower()

    #preliminary checks
    if len(guess) != 5:
        await msg_embed(ctx, "Guess must be a 5 letter word!")
        return

    if guess not in database.word_list:
        await msg_embed(ctx, "Word must be a valid english word!")
        return

    #get amount of each letter in guess
    d = dict(collections.Counter(answer))

    guess_result = guess_result_default # what letters they got right and wrong

    #loop through and detect green letters
    for count, letter in enumerate(guess):
        if answer[count] == letter:
            guess_result[count] = green_letters[letter]

            #remove letter counter
            if d[letter] > 0:
                d[letter] -= 1

    #yellow letters
    for count, letter in enumerate(guess):
        if answer[count] != letter and letter in answer:
            if d[letter] > 0:
                guess_result[count] = yellow_letters[letter]

                d[letter] -=1
            else:
                guess_result[count] = gray_letters[letter]

    #not found letters
    for count, letter in enumerate(guess):
        if letter not in answer:
            guess_result[count] = gray_letters[letter]

    game_data["guesses"].append("".join(guess_result))
    game_data["remaining-guesses"] -= 1

    won = guess == answer
    lost = game_data["remaining-guesses"] == 0 and not won

    await ctx.send(embed=get_wordle_embed(ctx, game_data, won, lost))

    if won or lost:
        if won:
            database.user_data.update_one({"_id": ctx.author.id}, {"$inc": {"balance": WORLD_REWARD(game_data["remaining-guesses"])}})

        del database.wordle_games[ctx.author.id]