"""
Config Command Cog
~~~~~~~~~~~~~~~~~~~

This cog contains the commands:
* info
* config
"""

import discord
from discord.ext import commands
from discord.ext.commands import Context
from src.util.constants import PREFIX
from src.util.embed_func import welcome_embed

# commandsz 
from src.commands.config.config import config_menu

# initialise class
class Config(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @commands.command(description="See the info message for this bot", usage=
    {
        "Syntax": f"{PREFIX}info"
    })
    async def info(self, ctx:Context):
        await ctx.send(embed=welcome_embed(self.bot))

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def config(self, ctx:Context):
        await config_menu(self.bot, ctx)

# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(Config(bot))