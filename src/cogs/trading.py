# This cog is for skin unboxing related commands
# Commands:
# * trade
# ** add
# ** remove
import discord
from discord.ext import commands
from discord.ext.commands import Context
from src.util.constants import PREFIX
from src.util import database

# initialise class
class Trading(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot:commands.Bot):
    await bot.add_cog(Trading(bot))