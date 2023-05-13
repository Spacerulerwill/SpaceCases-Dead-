"""
Copyright (C) 2023 William Redding - All Rights Reserved

See end of file for licence details
"""

import discord
import random
import collections
from discord.ext.commands import Context
from src.util.decorators import requires
from src.util.string_util import currency_str_format
from src.util.embed_func import msg_embed
from src.util import database
from src.lang.lang import get_locale_fm
from src.util.emojis import green_letters, yellow_letters, gray_letters, BLANK_LETTER

BLANK_ROW = BLANK_LETTER * 5 + "\n"
guess_result_default = [None for x in range(5)]

WORLDE_PRICE = 250
WORLD_REWARD = lambda remaining_guesses: WORLDE_PRICE + 500 + (remaining_guesses * 250)


def get_wordle_embed(
    lang: str, game_data: dict, won: bool = False, lost: bool = False
) -> discord.Embed:
    description = ""

    if won:
        title = get_locale_fm(
            lang,
            "wordle.won.embed.title",
            currency_str_format(WORLD_REWARD(game_data["remaining_guesses"])),
        )
        color = discord.Color.green()
    elif lost:
        title = get_locale_fm(lang, "wordle.loss.embed.title")
        description += get_locale_fm(
            lang, "wordle.loss.embed.description", game_data["answer"]
        )
        color = discord.Color.red()
    else:
        title = ""
        color = discord.Color.dark_theme()
    for guess in game_data["guesses"]:
        description += guess + "\n"

    for i in range(game_data["remaining_guesses"]):
        description += BLANK_ROW

    e = discord.Embed(title=title, color=color, description=description)

    return e


async def new_game(lang: str, ctx: Context) -> dict:
    # check user has enough to play
    update_result = database.user_data.update_one(
        {"_id": ctx.author.id},
        [
            {
                "$set": {
                    "balance": {
                        "$cond": {
                            "if": {"$gte": ["$balance", WORLDE_PRICE]},
                            "then": {"$subtract": ["$balance", WORLDE_PRICE]},
                            "else": "$balance",
                        }
                    }
                }
            }
        ],
    )

    if update_result.modified_count == 0:
        await msg_embed(ctx, get_locale_fm(lang, "not_enough_funds"))
        return None

    game_data = {
        "user_id": ctx.author.id,
        "answer": random.choice(database.word_list),
        "remaining_guesses": 6,
        "guesses": [],
    }

    return game_data


@requires(users_registered=True)
async def wordle(ctx: Context, guess: str):
    lang = database.user_data.find_one({"_id": ctx.author.id})["lang"]

    # no guess - just see current game, or create new one if none is started
    if guess is None:
        try:
            game_data = database.wordle_games[ctx.author.id]
        except KeyError:
            game_data = await new_game(lang, ctx)
            if game_data is None:
                return

            database.wordle_games[ctx.author.id] = game_data

        await ctx.send(embed=get_wordle_embed(lang, game_data))
    else:
        # they made a guess - play the game
        try:
            await guess_word(lang, ctx, guess)
        except KeyError:
            game_data = await new_game(lang, ctx)

            if game_data is None:
                return

            database.wordle_games[ctx.author.id] = game_data
            await guess_word(lang, ctx, guess)


# guess word logic
async def guess_word(lang: str, ctx: Context, guess: str):
    game_data = database.wordle_games[ctx.author.id]
    answer = game_data["answer"]

    guess = guess.lower()

    # preliminary checks
    if len(guess) != 5:
        await msg_embed(ctx, get_locale_fm(lang, "wordle.word_wrong_length"))
        return

    if guess not in database.word_list:
        await msg_embed(ctx, get_locale_fm(lang, "wordle.word_not_found"))
        return

    # get amount of each letter in guess
    d = dict(collections.Counter(answer))

    guess_result = guess_result_default  # what letters they got right and wrong

    # loop through and detect green letters
    for count, letter in enumerate(guess):
        if answer[count] == letter:
            guess_result[count] = green_letters[letter]

            # remove letter counter
            if d[letter] > 0:
                d[letter] -= 1

    # yellow letters
    for count, letter in enumerate(guess):
        if answer[count] != letter and letter in answer:
            if d[letter] > 0:
                guess_result[count] = yellow_letters[letter]

                d[letter] -= 1
            else:
                guess_result[count] = gray_letters[letter]

    # not found letters
    for count, letter in enumerate(guess):
        if letter not in answer:
            guess_result[count] = gray_letters[letter]

    game_data["guesses"].append("".join(guess_result))
    game_data["remaining_guesses"] -= 1

    won = guess == answer
    lost = game_data["remaining_guesses"] == 0 and not won

    await ctx.send(embed=get_wordle_embed(lang, game_data, won, lost))

    if won or lost:
        if won:
            database.user_data.update_one(
                {"_id": ctx.author.id},
                {"$inc": {"balance": WORLD_REWARD(game_data["remaining_guesses"])}},
            )

        del database.wordle_games[ctx.author.id]


"""
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.

                            Preamble

  The GNU General Public License is a free, copyleft license for
software and other kinds of works.

  The licenses for most software and other practical works are designed
to take away your freedom to share and change the works.  By contrast,
the GNU General Public License is intended to guarantee your freedom to
share and change all versions of a program--to make sure it remains free
software for all its users.  We, the Free Software Foundation, use the
GNU General Public License for most of our software; it applies also to
any other work released this way by its authors.  You can apply it to
your programs, too.

  When we speak of free software, we are referring to freedom, not
price.  Our General Public Licenses are designed to make sure that you
have the freedom to distribute copies of free software (and charge for
them if you wish), that you receive source code or can get it if you
want it, that you can change the software or use pieces of it in new
free programs, and that you know you can do these things.

  To protect your rights, we need to prevent others from denying you
these rights or asking you to surrender the rights.  Therefore, you have
certain responsibilities if you distribute copies of the software, or if
you modify it: responsibilities to respect the freedom of others.

  For example, if you distribute copies of such a program, whether
gratis or for a fee, you must pass on to the recipients the same
freedoms that you received.  You must make sure that they, too, receive
or can get the source code.  And you must show them these terms so they
know their rights.

  Developers that use the GNU GPL protect your rights with two steps:
(1) assert copyright on the software, and (2) offer you this License
giving you legal permission to copy, distribute and/or modify it.

  For the developers' and authors' protection, the GPL clearly explains
that there is no warranty for this free software.  For both users' and
authors' sake, the GPL requires that modified versions be marked as
changed, so that their problems will not be attributed erroneously to
authors of previous versions.

  Some devices are designed to deny users access to install or run
modified versions of the software inside them, although the manufacturer
can do so.  This is fundamentally incompatible with the aim of
protecting users' freedom to change the software.  The systematic
pattern of such abuse occurs in the area of products for individuals to
use, which is precisely where it is most unacceptable.  Therefore, we
have designed this version of the GPL to prohibit the practice for those
products.  If such problems arise substantially in other domains, we
stand ready to extend this provision to those domains in future versions
of the GPL, as needed to protect the freedom of users.

  Finally, every program is threatened constantly by software patents.
States should not allow patents to restrict development and use of
software on general-purpose computers, but in those that do, we wish to
avoid the special danger that patents applied to a free program could
make it effectively proprietary.  To prevent this, the GPL assures that
patents cannot be used to render the program non-free.

  The precise terms and conditions for copying, distribution and
modification follow.
"""
