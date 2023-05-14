"""
Copyright (C) 2022 William Redding - All Rights Reserved

See end of file for licence details
"""

from discord.ext.commands import Context
from src.util import database
from src.lang.lang import get_locale_fm
from src.util.string_util import (
    get_closest_match,
)
from src.util.embed_func import msg_embed
from src.util.item_func import get_item_embed


async def item(ctx: Context, *args):
    user_data = database.user_data.find_one({"_id": ctx.author.id})

    # if they have no user data - default language is english
    if user_data is None:
        lang = "en"
    else:
        lang = user_data["lang"]

    item_query = " ".join(args[:]).strip().lower()

    try:
        item_data = database.item_data["items"][item_query]
        print(item_data)
    except KeyError:
        # try and find closest match
        closest_match = get_closest_match(
            item_query, database.item_data["items"].keys()
        )

        # if match is reasonably close enough
        if closest_match is None:
            await msg_embed(ctx, get_locale_fm(lang, "item.not_found"))
        else:
            await msg_embed(
                ctx,
                get_locale_fm(
                    lang,
                    "item.not_found_suggest",
                    closest_match,
                ),
            )
        return

    e = get_item_embed(lang, item_data)
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