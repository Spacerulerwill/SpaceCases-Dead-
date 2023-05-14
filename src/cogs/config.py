"""
Copyright (C) 2023 William Redding - All Rights Reserved

Commands
~~~~~~~~
* info
* config

See end of file for licence details
"""

from discord.ext import commands
from discord.ext.commands import Context
from discord.ext.commands.bot import Bot

# command imports
from src.commands.config.config import config_menu
from src.commands.config.info import info

# initialise class
class Config(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def info(self, ctx: Context):
        await info(ctx)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def config(self, ctx: Context):
        await config_menu(ctx, self.bot)


# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot: Bot):
    await bot.add_cog(Config(bot))

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