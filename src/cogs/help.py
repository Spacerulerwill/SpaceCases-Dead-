"""
Copyright (C) 2022 William Redding - All Rights Reserved

Commands
~~~~~~~~
* help

See end of file for licence details
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


"""
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.

                            Preamble

  The GNU General Public License is a free, copyleft license for
software and other kinds of works.

  The licenses for most software and other practical works are designed
to take away your freedom to share and change the works.  By contrast,
the GNU General Public License is intended to guarantee your freedom to
share and change all versions of a program--to make sure it remains free
software for all its users.  We, the Free Software Foundation, use the
GNU General Public License for most of our software; it applies also to
any other work released this way by its authors.  You can apply it to
your programs, too.

  When we speak of free software, we are referring to freedom, not
price.  Our General Public Licenses are designed to make sure that you
have the freedom to distribute copies of free software (and charge for
them if you wish), that you receive source code or can get it if you
want it, that you can change the software or use pieces of it in new
free programs, and that you know you can do these things.

  To protect your rights, we need to prevent others from denying you
these rights or asking you to surrender the rights.  Therefore, you have
certain responsibilities if you distribute copies of the software, or if
you modify it: responsibilities to respect the freedom of others.

  For example, if you distribute copies of such a program, whether
gratis or for a fee, you must pass on to the recipients the same
freedoms that you received.  You must make sure that they, too, receive
or can get the source code.  And you must show them these terms so they
know their rights.

  Developers that use the GNU GPL protect your rights with two steps:
(1) assert copyright on the software, and (2) offer you this License
giving you legal permission to copy, distribute and/or modify it.

  For the developers' and authors' protection, the GPL clearly explains
that there is no warranty for this free software.  For both users' and
authors' sake, the GPL requires that modified versions be marked as
changed, so that their problems will not be attributed erroneously to
authors of previous versions.

  Some devices are designed to deny users access to install or run
modified versions of the software inside them, although the manufacturer
can do so.  This is fundamentally incompatible with the aim of
protecting users' freedom to change the software.  The systematic
pattern of such abuse occurs in the area of products for individuals to
use, which is precisely where it is most unacceptable.  Therefore, we
have designed this version of the GPL to prohibit the practice for those
products.  If such problems arise substantially in other domains, we
stand ready to extend this provision to those domains in future versions
of the GPL, as needed to protect the freedom of users.

  Finally, every program is threatened constantly by software patents.
States should not allow patents to restrict development and use of
software on general-purpose computers, but in those that do, we wish to
avoid the special danger that patents applied to a free program could
make it effectively proprietary.  To prevent this, the GPL assures that
patents cannot be used to render the program non-free.

  The precise terms and conditions for copying, distribution and
modification follow.
"""
