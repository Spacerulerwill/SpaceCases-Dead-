"""
Copyright (C) 2022 William Redding - All Rights Reserved

See end of file for licence details
"""

from discord.ext.commands import Context
from src.util import database
from src.lang.lang import get_locale_fm
from src.util.string_util import currency_str_format
from src.util.item_func import gen_item
from src.util.constants import ONE_DAY, rarity_color_dict
from src.util.embed_func import msg_embed
from src.util.decorators import requires
from datetime import datetime
import discord
import time
import random

# 14 days
CLAIM_MONEY_AMOUNTS = [
    5000,
    7500,
    10000,
    10000,
    12000,
    14000,
    16000,
    18000,
    20000,
    20000,
    22500,
    25000,
    27500,
    30000,
]

max_claim_streak = len(CLAIM_MONEY_AMOUNTS)

CLAIM_BONUS_REWARDS = {4: "classified", 10: "covert", 14: "rare items"}


@requires(users_registered=True)
async def claim(ctx: Context):
    datetime.now
    # update balance and set last claim to now if been twelve hours since last claim
    update_result = database.user_data.update_one(
        {"_id": ctx.author.id},
        [
            {
                "$set": {
                    "claim_streak": {
                        "$let": {
                            "vars": {
                                "daydiff": {
                                    "$subtract": [
                                        int(time.time()) // ONE_DAY,
                                        {
                                            "$trunc": [
                                                {"$divide": ["$last_claim", ONE_DAY]}
                                            ]
                                        },
                                    ]
                                }
                            },
                            "in": {
                                "$switch": {
                                    "branches": [
                                        {
                                            "case": {
                                                "$or": [
                                                    {"$eq": ["$last_claim", 0]},
                                                    {"$gt": ["$$daydiff", 1]},
                                                ]
                                            },
                                            "then": 1,
                                        },
                                        {
                                            "case": {"$eq": ["$$daydiff", 1]},
                                            "then": {"$add": ["$claim_streak", 1]},
                                        },
                                    ],
                                    "default": "$claim_streak",
                                }
                            },
                        }
                    },
                    "balance": {
                        "$let": {
                            "vars": {
                                "daydiff": {
                                    "$subtract": [
                                        int(time.time()) // ONE_DAY,
                                        {
                                            "$trunc": [
                                                {"$divide": ["$last_claim", ONE_DAY]}
                                            ]
                                        },
                                    ]
                                },
                                "claim_money_amounts": CLAIM_MONEY_AMOUNTS,
                            },
                            "in": {
                                "$cond": {  # if first claim ever, or streak broken, add the first money amount
                                    "if": {
                                        "$or": [
                                            {"$eq": ["$last_claim", 0]},
                                            {"$gt": ["$$daydiff", 1]},
                                        ]
                                    },
                                    "then": {
                                        "$add": [
                                            "$balance",
                                            {
                                                "$arrayElemAt": [
                                                    "$$claim_money_amounts",
                                                    0,
                                                ]
                                            },
                                        ]
                                    },
                                    "else": {  # otherwise if claim streak is greater than max, add the max
                                        "$cond": {
                                            "if": {"$eq": ["$$daydiff", 1]},
                                            "then": {
                                                "$cond": [
                                                    {
                                                        "$gte": [
                                                            "$claim_streak",
                                                            max_claim_streak,
                                                        ]
                                                    },
                                                    {
                                                        "$add": [
                                                            "$balance",
                                                            {
                                                                "$arrayElemAt": [
                                                                    "$$claim_money_amounts",
                                                                    max_claim_streak
                                                                    - 1,
                                                                ]
                                                            },
                                                        ]
                                                    },
                                                    {
                                                        "$add": [
                                                            "$balance",
                                                            {
                                                                "$arrayElemAt": [
                                                                    "$$claim_money_amounts",
                                                                    "$claim_streak",
                                                                ]
                                                            },
                                                        ]
                                                    },
                                                ]
                                            },
                                            "else": "$balance",
                                        }
                                    },
                                }
                            },
                        }
                    },
                    "last_claim": {
                        "$let": {
                            "vars": {
                                "daydiff": {
                                    "$subtract": [
                                        int(time.time()) // ONE_DAY,
                                        {
                                            "$trunc": [
                                                {"$divide": ["$last_claim", ONE_DAY]}
                                            ]
                                        },
                                    ]
                                },
                                "claim_money_amounts": CLAIM_MONEY_AMOUNTS,
                            },
                            "in": {
                                "$cond": {
                                    "if": {
                                        "$or": [
                                            {"$gte": ["$$daydiff", 1]},
                                            {"$eq": ["$last_claim", 0]},
                                        ]
                                    },
                                    "then": int(time.time()),
                                    "else": "$last_claim",
                                }
                            },
                        }
                    },
                }
            }
        ],
    )

    # if document modified
    if update_result.modified_count == 1:
        post_doc = database.user_data.find_one({"_id": ctx.author.id})
        lang = post_doc["lang"]

        # create embed
        e = discord.Embed(
            title=get_locale_fm(lang, "claim.embed.title"),
            description=get_locale_fm(lang, "claim.embed.description"),
            color=discord.Color.green(),
        )
        e.set_thumbnail(url=ctx.author.display_avatar.url)

        footer = get_locale_fm(lang, "claim.embed.footer")

        view = None

        prev_streak = post_doc["claim_streak"]
        if prev_streak != 0:
            prev_streak -= 1

        if post_doc["claim_streak"] >= max_claim_streak:
            e.add_field(
                name=get_locale_fm(lang, "claim.embed.amount"),
                value="$300.00",
                inline=True,
            )
        else:
            e.add_field(
                name=get_locale_fm(lang, "claim.embed.amount"),
                value=currency_str_format(CLAIM_MONEY_AMOUNTS[prev_streak]),
                inline=True,
            )

        e.add_field(
            name=get_locale_fm(lang, "claim.embed.new_balance"),
            value=currency_str_format(post_doc["balance"]),
            inline=True,
        )
        e.add_field(
            name=get_locale_fm(lang, "claim.embed.streak"),
            value=post_doc["claim_streak"],
            inline=True,
        )

        bonus_reward = CLAIM_BONUS_REWARDS.get(post_doc["claim_streak"])

        interacted_with = False

        # callbacks
        async def sell_item():
            nonlocal interacted_with
            # change color to dark gray, remove footer, change balance to have balance of skin
            database.user_data.update_one(
                {"_id": ctx.author.id}, {"$inc": {"balance": skin_price}}
            )

            e.colour = discord.colour.Color.dark_gray()
            e.set_footer(text="")

            await msg.edit(embed=e, view=None)
            interacted_with = True

        async def sell_callback(interact: discord.Interaction):
            if ctx.author.id == interact.user.id:
                await sell_item()
            await interact.response.defer()

        async def inventory_callback(interact: discord.Interaction):
            nonlocal interacted_with
            if interact.user.id == ctx.author.id:
                # add to user inventory
                filter_ = {
                    "_id": ctx.author.id,
                    "$expr": {"$lt": ["$inventory_size", "$inventory_max_capacity"]},
                }
                update = {
                    "$push": {
                        "inventory": {"name": unformatted_name, "float": float_val}
                    },
                    "$inc": {"inventory_size": 1},
                }

                update_result = database.user_data.update_one(filter_, update)

                if update_result.modified_count == 1:
                    e.colour = discord.colour.Color.green()
                    e.set_footer(text="")
                    await msg.edit(embed=e, view=None)

                elif update_result.modified_count == 0:
                    await msg_embed(ctx, get_locale_fm(lang, "inventory.full"))
            await interact.response.defer()

        # if not interacted with after 30 seconds, sell the item
        async def view_timeout_callback():
            if not interacted_with:
                await sell_item()

        # if bonus item reward, pick random item of given quality
        if bonus_reward != None:
            footer += get_locale_fm(lang, "claim.embed.footer.bonus_item")

            # pick random case
            random_container = random.choice(list(database.containers.keys()))
            item_pool = database.containers[random_container]["items"][bonus_reward]
            unformatted_name, float_val = gen_item(random.choice(item_pool))

            skin_data = database.skin_data["skins"][unformatted_name]
            skin_price = skin_data["price"]

            e.add_field(
                name=get_locale_fm(lang, "claim.embed.bonus_item"),
                value=f"**{skin_data['formatted_name']}** - **{currency_str_format(skin_price)}**",
                inline=False,
            )
            e.color = rarity_color_dict[skin_data["rarity"]]
            e.set_image(url=skin_data["image_url"])

            # create view
            view = discord.ui.View()
            view.on_timeout = view_timeout_callback
            inventory_button = discord.ui.Button(
                label=get_locale_fm(lang, "button.add_to_inventory"),
                style=discord.ButtonStyle.green,
            )
            inventory_button.callback = inventory_callback
            sell_button = discord.ui.Button(
                label=get_locale_fm(lang, "button.sell"), style=discord.ButtonStyle.red
            )
            sell_button.callback = sell_callback
            view.add_item(inventory_button)
            view.add_item(sell_button)

        e.set_footer(text=footer)
        msg = await ctx.send(embed=e, view=view)

    else:
        lang = database.user_data.find_one({"_id": ctx.author.id})["language"]
        await msg_embed(ctx, get_locale_fm(lang, "claim.already"))


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
