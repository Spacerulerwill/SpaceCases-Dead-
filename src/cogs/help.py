"""
Help Command Cog
~~~~~~~~~~~~~~~~~~~

This cog contains the commands:
* Help
"""

import discord
from discord.ext import commands
from discord.ext.commands import Context
from src.util.constants import PREFIX
from src.lang.lang import get_locale_fm, get_locale
from src.util import database
from src.util.string_util import get_closest_match
from src.util.embed_func import msg_embed


# initialise class
class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # This command displays a menu with all cogs and their commands if no command is specified
    # If a command is specified with display the description and usage details of that command
    @commands.command()
    async def help(self, ctx: Context, *args):
        user_data = database.user_data.find_one({"_id": ctx.author.id})

        if user_data is None:
            lang = "en"
        else:
            lang = user_data["lang"]

        cmd_query = " ".join(args[:]).strip().lower()

        if cmd_query == "":
            e = discord.Embed(
                description=get_locale_fm(lang, "help.embed.description"),
                color=discord.Color.dark_theme(),
            )
            e.set_thumbnail(url=self.bot.user.display_avatar.url)

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
            try:
                cmd_query_splt = cmd_query.split(" ")

                # command
                if len(cmd_query_splt) == 1:
                    cmd_query_name = cmd_query_splt[0]
                    command: commands.Command = self.bot.get_command(cmd_query_name)
                    command_name = command.name

                    description: str = get_locale_fm(
                        lang, command_name + ".description"
                    )
                    usage: dict = get_locale(lang, command_name + ".usage")

                    e = discord.Embed(
                        title=f"{PREFIX}{command_name}",
                        description=description,
                        color=discord.Color.dark_theme(),
                    )
                    e.set_thumbnail(url=self.bot.user.display_avatar.url)

                    for name, value in usage.items():
                        e.add_field(name=name, value=value, inline=False)

                    if len(command.aliases) > 0:
                        alias_str = ""
                        for alias in command.aliases:
                            alias_str += f"\u200b\t•{alias}\n"
                        e.add_field(
                            name=get_locale_fm(lang, "help.aliases"),
                            value=alias_str,
                            inline=False,
                        )

                    await ctx.send(embed=e)

                elif len(cmd_query_splt) == 2:  # command with group
                    group_name = cmd_query_splt[0]
                    cmd_query_name = cmd_query_splt[1]
                    group: commands.Group = self.bot.get_command(group_name)
                    subcommand = group.get_command(cmd_query_name)
                    subcommand_name = subcommand.name

                    description: str = get_locale_fm(
                        lang, f"{group_name}_{subcommand_name}.description"
                    )
                    usage: dict = get_locale(
                        lang, f"{group_name}_{subcommand_name}.usage"
                    )

                    e = discord.Embed(
                        title=f"{PREFIX}{group_name} {subcommand_name}",
                        description=description,
                        color=discord.Color.dark_theme(),
                    )
                    e.set_thumbnail(url=self.bot.user.display_avatar.url)

                    for name, value in usage.items():
                        e.add_field(name=name, value=value, inline=False)

                    if len(subcommand.aliases) > 0:
                        alias_str = ""
                        for alias in subcommand.aliases:
                            alias_str += f"\u200b\t•{alias}\n"
                        e.add_field(
                            name=get_locale_fm(lang, "help.aliases"),
                            value=alias_str,
                            inline=False,
                        )

                    await ctx.send(embed=e)
            except AttributeError:
                closest_match = get_closest_match(
                    cmd_query_name, self.bot.all_commands.keys()
                )
                if closest_match is None:
                    await msg_embed(ctx, get_locale_fm(lang, "command_not_found"))
                else:
                    await msg_embed(
                        ctx,
                        get_locale_fm(lang, "command_not_found_suggest", closest_match),
                    )


# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(Help(bot))
