"""
Copyright (C) 2023 William Redding - All Rights Reserved

Room related functionality

Functions
~~~~~~~~~
* delete_room
* get_guild_room_create_channel

See end of file for licence details
"""

import asyncio
import discord
from src.util import database
from src.util.constants import ROOM_DELETION_TIME

from dataclasses import dataclass


@dataclass
class Room:
    thread: discord.Thread
    task: asyncio.Task


async def delete_room(owner_id: int, thread: discord.Thread):
    """Delete a room given its owner's discord id and the thread

    Args:
        owner_id: the user id of the owner of the room
        thread: the thread for the room
    """
    await asyncio.sleep(ROOM_DELETION_TIME)
    await thread.delete()
    database.rooms.pop(owner_id, None)


def get_guild_room_create_channel(guild: discord.Guild, guild_data=None):
    """Get the channel for the guild used for room creation, if not found inform database it has been deleted

    Args:
        guild: the guild
        guild_data: default: None - provide guild data if already accessed, guild data will be fetched again if not provided
    Returns:
        the channel used for room creation
        None if not found
    """
    if guild_data is None:
        guild_data = database.guild_data.find_one({"_id": guild.id})
        if guild_data is None:
            return None

    channel = guild.get_channel(guild_data["unbox_room_creation_channel_id"])
    if channel is None:
        database.guild_data.update_one(
            {"_id": guild.id}, {"$set": {"unbox_room_creation_channel_id": None}}
        )

    return channel


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
