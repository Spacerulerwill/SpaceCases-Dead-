from discord.ext.commands import Context
from src.util import database
from src.util.constants import PREFIX, ROOM_DELETION_TIME
from src.util.embed_func import msg_embed
from threading import Timer
import discord
import asyncio


async def room(ctx:Context):
    guild_data = database.guild_data.find_one({"_id": ctx.guild.id})

    if guild_data is None or guild_data["unbox-room-creation-channel-id"] is None:
        await msg_embed(ctx, f"This server does not have rooms set up yet. You can either unbox without a room, or ask an **admin** to use `{PREFIX} room` to set it up")
        return

    if ctx.channel.id != guild_data["unbox-room-creation-channel-id"]:
        channel = ctx.bot.get_channel(guild_data["unbox-room-creation-channel-id"])
        await msg_embed(ctx, f"You must be in {channel.mention} to create a room!")
        return

    thread:discord.Thread = await ctx.channel.create_thread(name=f"{ctx.author.name}'s room", type=discord.ChannelType.private_thread, auto_archive_duration=60)

    await msg_embed(ctx, f"{thread.mention} has been created. It will be deleted after 15 minutes of inactivity")

    async def delete_thread():
        await asyncio.sleep(ROOM_DELETION_TIME)

        #try delete thread
        try:
            await thread.delete()
        except:
            pass
        
    task = asyncio.create_task(delete_thread())
    database.rooms[ctx.author.id] = [thread, task]
