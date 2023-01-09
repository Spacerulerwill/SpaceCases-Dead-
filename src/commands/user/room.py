from discord.ext.commands import Context
from src.util import database
from src.util.embed_func import msg_embed
import discord

async def room(ctx:Context):
    user_data = database.user_data.find_one({"_id": ctx.author.id})
    guild_data = database.guild_data.find_one({"_id": ctx.guild.id})

    if guild_data is None or guild_data["unbox-room-creation-channel-id"] is None:
        return

    if ctx.channel.id != guild_data["unbox-room-creation-channel-id"]:
        return

    if ctx.channel.get_thread(user_data["room-id"]) is not None:
        return

    thread:discord.Thread = await ctx.channel.create_thread(name=f"{ctx.author.name}'s room", type=discord.ChannelType.private_thread, auto_archive_duration=60)
    database.user_data.update_one({"_id": ctx.author.id}, {"$set": {"room-id": thread.id}})

    await msg_embed(ctx, f"Your room has been created: {thread.mention}")

        

    