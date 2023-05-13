"""
Copyright (C) 2022 William Redding - All Rights Reserved

See end of file for licence details
"""

import discord
import random
import numpy as np
from decimal import Decimal
from discord.ext.commands import Context
from discord.errors import NotFound
from src.util import database
from src.lang.lang import get_locale_fm
from src.util.string_util import currency_str_format
from src.util.decorators import requires
from src.util.embed_func import msg_embed_response, msg_embed


@requires(users_registered=True)
async def ttt(ctx: Context, player2: discord.Member, bet: Decimal):
    lang = database.user_data.find_one({"_id": ctx.author.id})["lang"]

    if bet < 0:
        await msg_embed(ctx, get_locale_fm(lang, "cannot_bet_negative"))
        return

    amount = int(bet * Decimal("100"))

    if ctx.author.id == player2.id:
        await msg_embed(ctx, get_locale_fm(lang, "cannot_play_against_self"))
        return

    e = discord.Embed(
        title=get_locale_fm(lang, "ttt.embed.title"),
        description=get_locale_fm(lang, "ttt.embed.description"),
        color=discord.Color.dark_theme(),
    )

    has_wager = amount != 0

    if has_wager:
        e.description += get_locale_fm(
            lang, "ttt.embed.description_wager", currency_str_format(amount)
        )

    e.set_thumbnail(url=ctx.bot.user.display_avatar.url)
    e.set_footer(
        icon_url=ctx.author.display_avatar.url,
        text=get_locale_fm(lang, "ttt.embed.footer"),
    )

    view = discord.ui.View(timeout=180)

    game_started = False

    async def view_timeout_callback():
        if game_started:
            return

        try:
            await msg.delete()
        except NotFound:
            pass

    view.on_timeout = view_timeout_callback

    if has_wager:
        button_label = f"{player2.name} - {currency_str_format(amount)}"
    else:
        button_label = player2.name

    opponent_accept = discord.ui.Button(
        style=discord.ButtonStyle.gray, label=button_label, emoji="✅"
    )
    opponent_ready = False

    async def opponent_callback(interact: discord.Interaction):
        nonlocal opponent_ready, game_started

        if interact.user.id != player2.id:
            await msg_embed_response(
                interact.response,
                get_locale_fm(lang, "not_your_button"),
                ephemeral=True,
            )
            return

        game_started = True

        if has_wager:
            # try and take money from both players, if it fails, then someone hasn't got enough money
            update_result = database.user_data.update_many(
                {"_id": {"$in": [ctx.author.id, player2.id]}},
                [
                    {
                        "$set": {
                            "balance": {
                                "$cond": {
                                    "if": {"$gte": ["$balance", amount]},
                                    "then": {
                                        "$subtract": ["$balance", amount],
                                    },
                                    "else": "$balance",
                                }
                            },
                        }
                    }
                ],
            )

            if update_result.modified_count != 2:
                await msg_embed_response(
                    interact.response,
                    get_locale_fm(
                        lang,
                        "ttt.both_players_not_enough_funds",
                        currency_str_format(amount),
                    ),
                )
                return

        await start_game(lang, ctx, player2, amount, has_wager, msg, interact)

    opponent_accept.callback = opponent_callback

    view.add_item(opponent_accept)

    msg = await ctx.send(embed=e, view=view)


async def start_game(
    lang: str,
    ctx: Context,
    player2: discord.User,
    amount: int,
    has_wager: bool,
    msg: discord.Message,
    interact: discord.Interaction,
):
    players = [ctx.author, player2]
    random.shuffle(players)
    counters = ["❌", "⭕"]
    turn_index = 0
    moves = 0
    game_over = False
    winner = None

    board = [[None for i in range(3)] for i in range(3)]

    async def button_callback(interact: discord.Interaction):
        nonlocal turn_index, winner, game_over, moves

        if game_over:
            await interact.response.defer()
            return

        if interact.user not in players:
            await msg_embed_response(
                interact.response,
                get_locale_fm(lang, "not_your_button"),
                ephemeral=True,
            )
            return

        elif interact.user != players[turn_index]:
            await interact.response.defer()
            return

        button_index = int(interact.data["custom_id"])

        if board[button_index // 3][button_index % 3] is not None:
            await interact.response.defer()
            return

        board[button_index // 3][button_index % 3] = counters[turn_index]
        buttons[button_index].emoji = counters[turn_index]
        moves += 1

        winner = checkWin(board)

        # check for win
        if winner is not None:
            game_over = True
            winner_user = players[counters.index(winner)]
            for button in buttons:
                button.disabled = True

            await interact.response.edit_message(
                content=get_locale_fm(lang, "ttt.player_won", winner_user.name),
                view=view,
            )

            if not has_wager:
                return

            # give money to winner user
            database.user_data.update_many(
                {"_id": winner_user.id}, {"$inc": {"balance": amount * 2}}
            )
            return

        elif moves == 9:
            game_over = True
            for button in buttons:
                button.disabled = True

            await interact.response.edit_message(
                content=get_locale_fm(lang, "ttt.draw"), view=view
            )

            if not has_wager:
                return

            # give both players money back
            database.user_data.update_many(
                {"_id": {"$in": [ctx.author.id, player2.id]}},
                {"$inc": {"balance": amount}},
            )
            return

        # if no win continue
        turn_index = (turn_index + 1) % 2

        await interact.response.edit_message(
            content=get_locale_fm(lang, "ttt.player_turn", players[turn_index].name),
            view=view,
        )

    view = discord.ui.View(timeout=10)

    # whoever it times out on, the other player wins
    async def game_timeout():
        nonlocal game_over, turn_index

        if game_over:
            return

        game_over = True

        turn_index = (turn_index + 1) % 2
        winner = counters[turn_index]
        winner_user = players[counters.index(winner)]

        for button in buttons:
            button.disabled = True

        if not has_wager:
            return

        # give money to winner user
        database.user_data.update_many(
            {"_id": winner_user.id}, {"$inc": {"balance": amount * 2}}
        )
        return

    view.on_timeout = game_timeout
    buttons = [
        discord.ui.Button(
            label="\u200b", style=discord.ButtonStyle.gray, row=i % 3, custom_id=str(i)
        )
        for i in range(9)
    ]

    for i in range(9):
        buttons[i].callback = button_callback
        view.add_item(buttons[i])

    await interact.response.edit_message(
        content=get_locale_fm(lang, "ttt.player_turn", players[turn_index].name),
        embed=None,
        view=view,
    )


def checkRows(board):
    for row in board:
        if len(set(row)) == 1:
            return row[0]
    return None


def checkDiagonals(board):
    if len(set([board[i][i] for i in range(len(board))])) == 1:
        return board[0][0]
    if len(set([board[i][len(board) - i - 1] for i in range(len(board))])) == 1:
        return board[0][len(board) - 1]
    return None


def checkWin(board):
    # transposition to check rows, then columns
    for newBoard in [board, np.transpose(board)]:
        result = checkRows(newBoard)
        if result:
            return result
    return checkDiagonals(board)


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
