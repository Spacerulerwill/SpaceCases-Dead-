# This cog is for skin unboxing related commands
# Commands:
# help

from csv import field_size_limit
import discord
from discord.ext import commands
from src.util.constants import PREFIX

# initialise class
class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx, command_name=None):
        if command_name == None:
            e = discord.Embed(description=f'Use `{PREFIX}help <command>` to gain more information about that command')

            for cog in self.bot.cogs:
                if cog != "Help":
                    field_value = ""
                    for command in self.bot.get_cog(cog).get_commands():
                        field_value += command.name + "\n"
                    e.add_field(name=cog, value=field_value)

            await ctx.send(embed=e)
        else:
            command = self.bot.get_command(command_name)
            if command == None:
                await ctx.send("Invalid command!")
                return
            e = discord.Embed(description=command.description)
            e.add_field(name="Usage", value=command.usage)
            await ctx.send(embed=e)

# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(Help(bot))