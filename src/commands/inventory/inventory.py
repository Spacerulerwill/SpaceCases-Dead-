"""
Copyright (C) 2022 William Redding - All Rights Reserved

See end of file for licence details
"""

import discord
from discord.ext.commands import Context
from src.util.constants import INVENTORY_ELEMS_PER_PAGE, rarity_emoji_dict
from src.util.decorators import requires
from src.util.embed_func import msg_embed, msg_embed_response
from src.util import database
from src.lang.lang import get_locale_fm
from src.util.string_util import currency_str_format


@requires(users_registered=True)
async def inventory(ctx: Context, member: discord.Member, page: int):
    if member == None:
        member = ctx.author

    user_data = database.user_data.find_one({"_id": member.id})
    lang = user_data["lang"]

    # if users inventory is empty
    if len(user_data["inventory"]) == 0:
        e = discord.Embed(
            title=get_locale_fm(lang, "inventory.embed.empty_title", member.name),
            color=discord.Color.dark_theme(),
        )
        e.set_thumbnail(url=member.display_avatar.url)

        if member == ctx.author:
            e.description = get_locale_fm(lang, "inventory.empty_1")
        else:
            e.description = get_locale_fm(lang, "inventory.empty_2", member.name)
        await ctx.send(embed=e)
        return

    # split into even chunks for pages
    inventory_data = list(user_data["inventory"])
    inventory_pages = [
        inventory_data[x : x + INVENTORY_ELEMS_PER_PAGE]
        for x in range(0, len(inventory_data), INVENTORY_ELEMS_PER_PAGE)
    ]

    if page <= 0 or page > len(inventory_pages):
        await msg_embed(ctx, get_locale_fm(lang, "invalid_page_number"))
        return

    page -= 1
    inventory_value = sum(
        [database.skin_data["skins"][item["name"]]["price"] for item in inventory_data]
    )

    # get inventory embed by function
    async def get_inventory_embed() -> discord.Embed:
        inventory_page = inventory_pages[page]

        string = ""
        for count, item in enumerate(inventory_page):
            skin_data = database.skin_data["skins"][item["name"]]
            emoji = rarity_emoji_dict[skin_data["rarity"]]
            string += get_locale_fm(
                lang,
                "inventory.item_string",
                emoji,
                count + (page * INVENTORY_ELEMS_PER_PAGE) + 1,
                skin_data["formatted_name"],
                currency_str_format(skin_data["price"]),
            )

        e = discord.Embed(
            title=get_locale_fm(
                lang,
                "inventory.embed.title",
                member.name,
                page + 1,
                len(inventory_pages),
            ),
            description=get_locale_fm(
                lang,
                "inventory.embed.description",
                currency_str_format(inventory_value),
                user_data["inventory_size"],
                user_data["inventory_max_capacity"],
            ),
            color=discord.Color.dark_theme(),
        )

        e.set_thumbnail(url=member.display_avatar.url)
        e.add_field(name="Contents", value=string)

        if member is ctx.author:
            e.add_field(
                name=get_locale_fm(lang, "commands"),
                value=get_locale_fm(lang, "inventory.embed.commands_1"),
                inline=False,
            )
        else:
            e.add_field(
                name=get_locale_fm(lang, "commands"),
                value=get_locale_fm(lang, "inventory.embed.commands_1"),
                inline=False,
            )

        return e

    # view and button callbacks
    async def prev_callback(interact: discord.Interaction):
        if interact.user.id != ctx.author.id:
            await msg_embed_response(
                interact.response,
                get_locale_fm(lang, "not_your_button"),
                ephemeral=True,
            )
            return

        nonlocal page

        if page == 0:
            page = len(inventory_pages) - 1
        else:
            page -= 1

        await interact.response.edit_message(
            embed=await get_inventory_embed(), view=view
        )

    async def next_callback(interact: discord.Interaction):
        if interact.user.id != ctx.author.id:
            await msg_embed_response(
                interact.response,
                get_locale_fm(lang, "not_your_button"),
                ephemeral=True,
            )
            return

        nonlocal page

        if page == len(inventory_pages) - 1:
            page = 0
        else:
            page += 1

        await interact.response.edit_message(
            embed=await get_inventory_embed(), view=view
        )

    view = None

    # only need buttons if inventory pages greater than 1
    if len(inventory_pages) > 1:
        view = discord.ui.View()
        prev_button = discord.ui.Button(label="◀", style=discord.ButtonStyle.gray)
        prev_button.callback = prev_callback
        next_button = discord.ui.Button(label="▶", style=discord.ButtonStyle.gray)
        next_button.callback = next_callback
        view.add_item(prev_button)
        view.add_item(next_button)

    await ctx.send(embed=await get_inventory_embed(), view=view)


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
