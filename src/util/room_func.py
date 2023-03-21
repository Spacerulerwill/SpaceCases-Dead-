import asyncio
import discord
from src.util import database
from src.util.constants import ROOM_DELETION_TIME

async def delete_room(owner_id:int, thread:discord.Thread):
    """Randomly generate a float and condition for a skin given its name, and determine if it's statrak

    Args:
        unformatted_name: the unformatted name of the skin
    Returns:
        a tuple of the new skin name and its float value
    """
    await asyncio.sleep(ROOM_DELETION_TIME)
    await thread.delete()
    database.rooms.pop(owner_id, None)

def get_guild_room_create_channel(guild:discord.Guild, guild_data=None):
    """Randomly generate a float and condition for a skin given its name, and determine if it's statrak

    Args:
        unformatted_name: the unformatted name of the skin
    Returns:
        a tuple of the new skin name and its float value
    """
    if guild_data is None:
        guild_data  = database.guild_data.find_one({"_id": guild.id})
        if guild_data is None:
            return None

    channel = guild.get_channel(guild_data["unbox-room-creation-channel-id"])
    if channel is None:
        database.guild_data.update_one({"_id": guild.id}, {"$set": {"unbox-room-creation-channel-id": None}})
    
    return channel

    
    

