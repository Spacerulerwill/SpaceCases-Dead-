"""
Copyright (C) 2022 William Redding - All Rights Reserved

See end of file for licence details
"""

import discord
from src.util import database
from src.lang.lang import get_locale_fm
from src.util.decorators import requires
from src.util.item_func import get_item_embed
from src.util.embed_func import msg_embed
from discord.ext.commands import Context


@requires(users_registered=True)
async def inspect(ctx: Context, member: discord.Member, item_index: int):
    if member is None:
        member = ctx.author

    user_data = database.user_data.find_one({"_id": member.id})
    lang = user_data["lang"]
    user_inventory = list(user_data["inventory"])

    if item_index > len(user_inventory):
        await msg_embed(
            ctx, get_locale_fm(lang, "inventory.not_found_index", item_index)
        )
        return

    item_index -= 1

    item = user_inventory[item_index]

    unformatted_name = item["name"]
    item_data = database.item_data["items"][unformatted_name]
    e = get_item_embed(lang, item_data)

    if item_data["item_type"] == "weapon":
        e.add_field(name=get_locale_fm(lang, "float"), value=str(item["float"]))

    e.set_footer(
        icon_url=member.display_avatar.url, text=f"This item belongs to {member.name}"
    )

    await ctx.send(embed=e)


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
