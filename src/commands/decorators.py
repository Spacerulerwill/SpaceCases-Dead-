from discord.ext.commands import Context
from src.util.constants import PREFIX
from src.util import database
import discord

def requires(users_registered:bool=False):
    def decorator(function):
        async def wrapper(*args, **kwargs):
            ctx, *_ = args
            ctx:Context

            # ensure all users in call are registered before proceeding
            if users_registered:
                if database.user_data.find_one({"_id": ctx.author.id}) is None:
                    await ctx.send(f"You are not registered! Use `{PREFIX}register` to register")
                    return

                for arg in _:
                    if isinstance(arg, discord.Member):
                        if database.user_data.find_one({"_id": arg.id}) is None:
                            await ctx.send(f"{arg.name} is not registered!")
                            return

            await function(*args, **kwargs)
        return wrapper
    return decorator