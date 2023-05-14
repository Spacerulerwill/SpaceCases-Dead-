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
        [database.item_data["items"][item["name"]]["price"] for item in inventory_data]
    )

    # get inventory embed by function
    async def get_inventory_embed() -> discord.Embed:
        inventory_page = inventory_pages[page]

        string = ""
        for count, item in enumerate(inventory_page):
            skin_data = database.item_data["items"][item["name"]]
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