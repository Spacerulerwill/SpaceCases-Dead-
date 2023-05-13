"""
Copyright (C) 2023 William Redding - All Rights Reserved

See end of file for licence details
"""

import discord
from discord.errors import NotFound
import random
from src.lang.lang import get_locale_fm
from discord.ext.commands import Context
from src.util.embed_func import msg_embed, msg_embed_response
from src.util.decorators import requires
from src.util.string_util import currency_str_format
from src.util.constants import (
    conditions,
    COSTS_MORE,
    COSTS_LESS,
    HL_MIN_GUESS,
    HL_MAX_GUESS,
    HL_PRICE,
    HL_REWARD,
)
from src.util import database


@requires(users_registered=True)
async def higher_lower(ctx: Context, difficulty: int):
    lang = database.user_data.find_one({"_id": ctx.author.id})["lang"]

    if not HL_MIN_GUESS <= difficulty <= HL_MAX_GUESS:
        await msg_embed(
            ctx,
            get_locale_fm(lang, "hl.invalid_difficulty"),
        )
        return

    # create start embed
    initial_item = random.choice(list(database.skin_data_hl.keys()))
    initial_item_data = database.skin_data_hl[initial_item]

    game_started = False

    e = discord.Embed(
        title=get_locale_fm(lang, "hl.embed.title"),
        description=get_locale_fm(lang, "hl.embed.description", difficulty),
        color=discord.Color.dark_theme(),
    )

    e.description += "**"
    if "Souvenir" in initial_item_data["formatted_name"]:
        e.description += "Souvenir "
    if "StatTrak" in initial_item_data["formatted_name"]:
        e.description += "StatTrak "
    e.description += f'{conditions[initial_item_data["condition_index"]]}'
    e.description += "**"

    e.set_image(url=initial_item_data["image_url"])
    e.set_footer(
        icon_url=ctx.author.display_avatar.url,
        text=get_locale_fm(lang, "hl.embed.footer"),
    )

    view = discord.ui.View(timeout=30)

    async def view_timeout_callback():
        try:
            if not game_started:
                await msg.delete()
        except NotFound:
            pass

    view.on_timeout = view_timeout_callback

    start_button = discord.ui.Button(
        label=get_locale_fm(lang, "button.start"), style=discord.ButtonStyle.green
    )

    # start game
    async def start_callback(interact: discord.Interaction):
        if interact.user.id != ctx.author.id:
            await msg_embed_response(
                interact.response,
                get_locale_fm(lang, "not_your_button"),
                ephemeral=True,
            )
            return

        nonlocal game_started
        game_started = True
        await interact.response.defer()
        await start_game(lang, ctx, difficulty, initial_item_data, msg)

    start_button.callback = start_callback
    view.add_item(start_button)

    msg = await ctx.send(embed=e, view=view)


async def start_game(
    lang: str,
    ctx: Context,
    difficulty: int,
    initial_skin_data: dict,
    msg: discord.Message,
):
    # check user has enough to play
    update_result = database.user_data.update_one(
        {"_id": ctx.author.id},
        [
            {
                "$set": {
                    "balance": {
                        "$cond": {
                            "if": {"$gte": ["$balance", HL_PRICE]},
                            "then": {"$subtract": ["$balance", HL_PRICE]},
                            "else": "$balance",
                        }
                    }
                }
            }
        ],
    )

    if update_result.modified_count == 0:
        await msg_embed(ctx, get_locale_fm(lang, "not_enough_funds"))
        return

    # get all skins prices
    random_skins = [
        random.choice(list(database.skin_data_hl.keys())) for x in range(difficulty)
    ]
    skin_data = [initial_skin_data] + [
        database.skin_data_hl[skin] for skin in random_skins
    ]
    correct_guesses = [
        skin_data[x]["price"] > skin_data[x - 1]["price"]
        for x in range(1, difficulty + 1)
    ]

    # view
    view = discord.ui.View(timeout=10)

    game_over = False

    # if button times out, the player has lost
    async def view_timeout_callback():
        if not game_over:
            e = discord.Embed(
                title=get_locale_fm(lang, "hl.playing.lost.embed.title"),
                description=get_locale_fm(lang, "hl.playing.lost.embed.out_of_time"),
                color=discord.Color.red(),
            )
            await msg.edit(embed=e, view=None)

    view.on_timeout = view_timeout_callback

    less_button = discord.ui.Button(
        label=get_locale_fm(lang, "button.less"), style=discord.ButtonStyle.red
    )
    more_button = discord.ui.Button(
        label=get_locale_fm(lang, "button.more"), style=discord.ButtonStyle.green
    )

    # call backs
    async def less_callback(interact: discord.Interaction):
        nonlocal guess_num, game_over

        if interact.user.id != ctx.author.id:
            await msg_embed_response(
                interact.response,
                get_locale_fm(lang, "not_your_button"),
                ephemeral=True,
            )
            return

        if guess_num + 1 < difficulty:
            if correct_guesses[guess_num] == COSTS_LESS:
                guess_num += 1
                await interact.response.edit_message(embed=get_embed(), view=view)
            else:
                game_over = True
                e = discord.Embed(
                    title=get_locale_fm(lang, "hl.playing.lost.embed.title"),
                    description=get_locale_fm(
                        lang,
                        "hl.playing.lost.embed.incorrect_guess",
                        skin_data[guess_num]["formatted_name"],
                        currency_str_format(skin_data[guess_num]["price"]),
                        skin_data[guess_num + 1]["formatted_name"],
                        currency_str_format(skin_data[guess_num + 1]["price"]),
                    ),
                    color=discord.Color.red(),
                )
                await msg.edit(embed=e, view=None)
        else:
            # they made it to last one - they have won!
            game_over = True
            amount_won = HL_REWARD(difficulty)

            e = discord.Embed(
                title=get_locale_fm(lang, "hl.playing.won.embed.title"),
                description=get_locale_fm(
                    lang,
                    "hl.playing.won.embed.description",
                    currency_str_format(amount_won),
                ),
                color=discord.Color.green(),
            )

            database.user_data.update_one(
                {"_id": ctx.author.id}, {"$inc": {"balance": amount_won}}
            )
            await msg.edit(embed=e, view=None)

    async def more_callback(interact: discord.Interaction):
        nonlocal guess_num, game_over
        if interact.user.id != ctx.author.id:
            await msg_embed_response(
                interact.response,
                get_locale_fm(lang, "not_your_button"),
                ephemeral=True,
            )
            return

        if guess_num + 1 < difficulty:
            if correct_guesses[guess_num] == COSTS_MORE:
                guess_num += 1
                await interact.response.edit_message(embed=get_embed(), view=view)
            else:
                game_over = True
                e = discord.Embed(
                    title=get_locale_fm(lang, "hl.playing.lost.embed.title"),
                    description=get_locale_fm(
                        lang,
                        "hl.playing.lost.embed.incorrect_guess",
                        skin_data[guess_num]["formatted_name"],
                        currency_str_format(skin_data[guess_num]["price"]),
                        skin_data[guess_num + 1]["formatted_name"],
                        currency_str_format(skin_data[guess_num + 1]["price"]),
                    ),
                    color=discord.Color.red(),
                )
                await msg.edit(embed=e, view=None)
        else:
            # they made it to last one - they have won!
            game_over = True
            amount_won = HL_REWARD(difficulty)

            e = discord.Embed(
                title=get_locale_fm(lang, "hl.playing.won.embed.title"),
                description=get_locale_fm(
                    lang,
                    "hl.playing.won.embed.description",
                    currency_str_format(amount_won),
                ),
                color=discord.Color.green(),
            )

            database.user_data.update_one(
                {"_id": ctx.author.id}, {"$inc": {"balance": amount_won}}
            )
            await msg.edit(embed=e, view=None)

    less_button.callback = less_callback
    more_button.callback = more_callback

    view.add_item(less_button)
    view.add_item(more_button)

    guess_num = 0

    def get_embed() -> discord.Embed:
        e = discord.Embed(
            title=get_locale_fm(
                lang, "hl.playing.embed.title", guess_num + 1, difficulty
            ),
            description=get_locale_fm(lang, "hl.playing.embed.description"),
        )

        e.description += "**"
        if "Souvenir" in skin_data[guess_num + 1]["formatted_name"]:
            e.description += "Souvenir "
        if "StatTrak" in skin_data[guess_num + 1]["formatted_name"]:
            e.description += "StatTrak "
        e.description += f'{conditions[skin_data[guess_num+1]["condition_index"]]}'
        e.description += "**"
        e.set_image(url=skin_data[guess_num + 1]["image_url"])
        return e

    await msg.edit(embed=get_embed(), view=view)


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
