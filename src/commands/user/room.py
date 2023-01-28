from discord.ext.commands import Context
from src.util import database
from src.util.constants import PREFIX, ROOM_DELETION_TIME
from src.util.embed_func import msg_embed
from src.util.decorators import requires
from src.util.room_func import delete_room, get_guild_room_create_channel
import discord
import asyncio

@requires(users_registered=True)
async def room(ctx:Context, public_private:str):

    try:
        guild_data = database.guild_data.find_one({"_id": ctx.guild.id})
    except AttributeError:
        await msg_embed(ctx, "You cannot create rooms here!")
        return

    room_creation_channel = get_guild_room_create_channel(ctx.guild, guild_data)
    if guild_data is None or guild_data["unbox-room-creation-channel-id"] is None or room_creation_channel is None:
        await msg_embed(ctx, f"This server does not have rooms set up yet. You can either unbox without a room, or ask an **admin** to use `{PREFIX}room` to set it up")
        return

    if ctx.channel.id != guild_data["unbox-room-creation-channel-id"]:
        await msg_embed(ctx, f"You must be in {room_creation_channel.mention} to create a room!")
        return

    room = database.rooms.get(ctx.author.id)
    if room is not None:   

        # if room is in a different guild, delete room but don't cancel auto deletion task - we want the old room to still delete itself after 15 minutes
        if ctx.guild.id != room[0].guild.id:
            database.rooms.pop(ctx.author.id, None)
        else:
            await msg_embed(ctx, f"{room[0].mention} already exists")
            return
    
    if public_private == "public":
        thread_type = discord.ChannelType.public_thread
    else:
        thread_type = discord.ChannelType.private_thread

    thread:discord.Thread = await ctx.channel.create_thread(name=f"{ctx.author.name}'s room", type=thread_type)

    if public_private == "private":
        await msg_embed(ctx, "Your private room has been created!")
        
    await msg_embed(thread, f"Welcome to your room {ctx.author.mention}! It will be deleted after 15 minutes of inactivity")
    await thread.add_user(ctx.author)
    
    task = asyncio.create_task(delete_room(ctx.author.id, thread))
    database.rooms[ctx.author.id] = [thread, task]