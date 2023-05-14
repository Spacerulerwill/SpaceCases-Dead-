"""
Copyright (C) 2023 William Redding - All Rights Reserved

See end of file for licence details
"""

from discord.ext.commands import Context
from src.util import database
from src.lang.lang import get_locale_fm
from src.util.embed_func import msg_embed
from src.util.decorators import requires
from src.util.room_func import delete_room, get_guild_room_create_channel, Room
import discord
import asyncio


@requires(users_registered=True)
async def room(ctx: Context, public_private: str):
    lang = database.user_data.find_one({"_id": ctx.author.id})["lang"]

    try:
        guild_data = database.guild_data.find_one({"_id": ctx.guild.id})
    except AttributeError:
        # if there is no ctx.guild ( i.e. in a dm )
        await msg_embed(ctx, get_locale_fm(lang, "room.cannot_create_here"))
        return

    room_creation_channel = get_guild_room_create_channel(ctx.guild, guild_data)
    if (
        guild_data is None
        or guild_data["unbox_room_creation_channel_id"] is None
        or room_creation_channel is None
    ):
        await msg_embed(ctx, get_locale_fm(lang, "room.not_setup"))
        return

    if ctx.channel.id != guild_data["unbox_room_creation_channel_id"]:
        await msg_embed(
            ctx,
            get_locale_fm(lang, "room.not_in_channel", room_creation_channel.mention),
        )
        return

    room = database.rooms.get(ctx.author.id)
    if room is not None:
        # if room is in a different guild, delete room but don't cancel auto deletion task - we want the old room to still delete itself after 15 minutes
        if ctx.guild.id != room[0].guild.id:
            database.rooms.pop(ctx.author.id, None)
        else:
            await msg_embed(ctx, get_locale_fm(lang, "room.exists", room[0].mention))
            return

    if public_private == "public":
        thread_type = discord.ChannelType.public_thread
    else:
        thread_type = discord.ChannelType.private_thread

    thread: discord.Thread = await ctx.channel.create_thread(
        name=f"{ctx.author.name}'s room", type=thread_type
    )

    if public_private == "private":
        await msg_embed(ctx, get_locale_fm(lang, "room.private_created"))

    await msg_embed(thread, get_locale_fm(lang, "room.greeting", ctx.author.mention))
    await thread.add_user(ctx.author)

    task = asyncio.create_task(delete_room(ctx.author.id, thread))
    database.rooms[ctx.author.id] = Room(thread, task)


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
