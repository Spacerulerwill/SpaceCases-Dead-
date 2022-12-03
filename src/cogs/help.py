# This cog is for skin unboxing related commands
# Commands:
# help

import discord
from discord.ext import commands
from discord.ext.commands import Context
from src.util.constants import PREFIX

# initialise class
class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # This command displays a menu with all cogs and their commands if no command is specified
    # If a command is specified with display the description and usage details of that command
    @commands.command()
    async def help(self, ctx:Context, *args):

        command_name = " ".join(args[:]).strip().lower()

        if command_name == "":
            e = discord.Embed(description=f'Use `{PREFIX}help <command>` to gain more information about that command')

            for cog in self.bot.cogs:
                if cog != "Help":
                    field_value = ""
                    for command in self.bot.get_cog(cog).get_commands():
                        # if its a command group
                        if isinstance(command, commands.Group):
                            field_value += command.name + "\n"
                            for command in command.commands:
                                field_value += f"\u200b\t• {command.name}\n"
                        else:
                            field_value += command.name + "\n"
                    e.add_field(name=cog, value=field_value)

            await ctx.send(embed=e)
        else:
            if command_name == "help":
                await ctx.send("Invalid command!")
                return
                
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