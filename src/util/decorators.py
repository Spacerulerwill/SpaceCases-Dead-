from discord.ext.commands import Context
from src.util.constants import PREFIX
from src.util.embed_func import msg_embed
from src.util import database
import discord

def requires(room:bool=False, users_registered:bool=False):
    """
    Requrires decorator - used for checking prerequisites for commands
    * users registered - all users must be registered before command usage
    * room - whether the command needs to be in a room for usage ( only applies if rooms are enabled )
    """
    def decorator(function):
        async def wrapper(*args, **kwargs):
            ctx, *_ = args
            ctx:Context

            if room:
                guild_data = database.guild_data.find_one({"_id": ctx.guild.id})

                HAS_GUILD_DATA = guild_data is not None and guild_data["unbox-room-creation-channel-id"] is not None
                if HAS_GUILD_DATA:
                    INVALID_PARENT_CHANNEL = hasattr(ctx.channel, "parent") and ctx.channel.parent.id != guild_data["unbox-room-creation-channel-id"]
                    NO_PARENT_CHANNEL = hasattr(ctx.channel, "parent") is False

                    if INVALID_PARENT_CHANNEL or NO_PARENT_CHANNEL:
                        channel = ctx.guild.get_channel(guild_data["unbox-room-creation-channel-id"])
                        await msg_embed(ctx, f"This command must be used in a room! Go to {channel.mention} and use `{PREFIX}room`")
                        return

            # ensure all users in call are registered before proceeding
            if users_registered:
                if database.user_data.find_one({"_id": ctx.author.id}) is None:
                    await msg_embed(ctx, f"You are not registered! Use `{PREFIX}register` to register")
                    return

                for arg in _:
                    if isinstance(arg, discord.Member):
                        if database.user_data.find_one({"_id": arg.id}) is None:
                            await msg_embed(ctx, f"{arg.name} is not registered!")
                            return

            await function(*args, **kwargs)
        return wrapper
    return decorator