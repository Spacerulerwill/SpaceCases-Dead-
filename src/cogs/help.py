# This cog is for skin unboxing related commands
# Commands:
# help

import discord
from discord.ext import commands
from discord.ext.commands import Context
from src.util.constants import PREFIX

# initialise class
class Help(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
    
    # This command displays a menu with all cogs and their commands if no command is specified
    # If a command is specified with display the description and usage details of that command
    @commands.command()
    async def help(self, ctx:Context, *args):
        command_name = " ".join(args[:]).strip().lower()

        if command_name == "":
            e = discord.Embed(description=f'Use `{PREFIX}help <command>` to gain more information about that command', color=discord.Color.dark_theme())

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
            command_name = command_name.split(" ")  
            
            #command
            if len(command_name) == 1:
                command_name = command_name[0]
                command:commands.Command = self.bot.get_command(command_name)
                if command == None or command.name == "help":
                    await ctx.send("Invalid command!")
                    return
                e = discord.Embed(description=command.description, color=discord.Color.dark_theme())
                e.add_field(name="Usage", value=command.usage)

                if len(command.aliases) > 0:
                    alias_str = ""
                    for alias in command.aliases:
                        alias_str += f"\u200b\t•{alias}\n"
                    e.add_field(name="Aliases", value=alias_str, inline=False)

                await ctx.send(embed=e)

            elif len(command_name) == 2: # command with group
                group_name = command_name[0]
                subcommand_name = command_name[1]
                group:commands.Group = self.bot.get_command(group_name)
                subcommand = group.get_command(subcommand_name)
                e = discord.Embed(description=subcommand.description, color=discord.Color.dark_theme())
                e.add_field(name="Usage", value=subcommand.usage)

                if len(subcommand.aliases) > 0:
                    alias_str = ""
                    for alias in subcommand.aliases:
                        alias_str += f"\u200b\t•{alias}\n"
                    e.add_field(name="Aliases", value=alias_str, inline=False)

                await ctx.send(embed=e)
            else:
                await ctx.send("Invalid command!")

# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(Help(bot))