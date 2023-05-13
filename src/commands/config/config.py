"""
Copyright (C) 2023 William Redding - All Rights Reserved

See end of file for licence details
"""

import discord
from discord.ext.commands import Context, Bot, TextChannelConverter
from src.util import database
from src.lang.lang import get_locale_fm
from pymongo import ReturnDocument
from src.util.decorators import requires
from src.util.embed_func import msg_embed, create_msg_embed, msg_embed_response
import asyncio

config_options = [
    {
        "name": "config.options.room_channel.name",
        "value": "unbox_room_creation_channel_id",
        "default_value": None,
        "type": discord.TextChannel,
        "description": "config.options.room_channel.description",
        "options": [],
        "response_text": "config.options.room_channel.response_embed_text",
        "post_func": lambda result: result.id,
    },
]


@requires(users_registered=True)
async def config_menu(ctx: Context, bot: Bot):
    user_data = database.user_data.find_one({"_id": ctx.author.id})

    if user_data is None:
        lang = "en"
    else:
        lang = user_data["lang"]

    option_index = 0

    async def get_config_embed() -> discord.Embed:
        post_doc = database.guild_data.find_one_and_update(
            {"_id": ctx.guild.id},
            {
                "$setOnInsert": {
                    "unbox_room_creation_channel_id": None,
                }
            },
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

        option = config_options[option_index]
        current_value = post_doc[option["value"]]

        match option["type"]:
            case discord.TextChannel:
                if current_value is not None:
                    try:
                        current_value = bot.get_channel(
                            post_doc[option["value"]]
                        ).mention
                    except AttributeError:
                        # channel no longer exists
                        current_value = get_locale_fm(lang, "backtick_none")
                        database.guild_data.update_one(
                            {"_id": ctx.guild.id}, {"$set": {option["value"]: None}}
                        )
                else:
                    current_value = get_locale_fm(lang, "backtick_none")
            case _:
                current_value = f"`{current_value}`"

        description = f"""{get_locale_fm(lang, option["description"])}
        
        {get_locale_fm(lang, "config.current_value", current_value)}"""

        e = discord.Embed(
            title=f'**{get_locale_fm(lang, option["name"])}**',
            description=description,
            color=discord.Color.dark_theme(),
        )
        e.set_thumbnail(url=bot.user.display_avatar.url)
        e.set_footer(text=get_locale_fm(lang, "config.menu.footer"))

        return e

    # VIEW
    async def view_timeout_callback():
        await msg.delete()

    view = discord.ui.View()
    view.on_timeout = view_timeout_callback

    select_options = [
        discord.SelectOption(
            label=get_locale_fm(lang, config_options[0]["name"]), value=0
        )
    ]

    if len(config_options) > 1:
        select_options += [
            discord.SelectOption(
                label=get_locale_fm(lang, option["name"]), value=count + 1
            )
            for count, option in enumerate(config_options[1:])
        ]

    select = discord.ui.Select(options=select_options)

    # SELECT MENU
    async def select_callback(interact: discord.Interaction):
        if interact.user.id != ctx.author.id:
            await msg_embed_response(
                interact.response,
                get_locale_fm(lang, "not_your_select"),
                ephemeral=True,
            )
            return

        nonlocal option_index
        option_index = int(select.values[0])

        await interact.response.edit_message(embed=await get_config_embed())

    select.callback = select_callback

    edit_button = discord.ui.Button(
        label=get_locale_fm(lang, "button.edit"), style=discord.ButtonStyle.gray
    )

    async def edit_callback(interact: discord.Interaction):
        if interact.user.id != ctx.author.id:
            await msg_embed_response(
                interact.response,
                get_locale_fm(lang, "not_your_button"),
                ephemeral=True,
            )
            return

        selected_option = config_options[option_index]

        name = get_locale_fm(lang, selected_option["name"])

        # send response embed
        await msg_embed_response(
            interact.response, get_locale_fm(lang, selected_option["response_text"])
        )

        # if no options, must be a user input
        if len(selected_option["options"]) == 0:

            def check(message: discord.Message):
                return message.author == ctx.author and message.channel == ctx.channel

            try:
                response: discord.Message = await bot.wait_for(
                    "message", check=check, timeout=30
                )

                if response:
                    # choose right conversion for each type
                    match selected_option["type"]:
                        case discord.TextChannel:
                            converter = lambda msg: TextChannelConverter().convert(
                                ctx, msg
                            )
                        case _:
                            converter = selected_option["type"]

                    # try conversion
                    try:
                        result = await converter(response.content)

                        # apply post func if neccesary
                        if selected_option["post_func"] is not None:
                            result = selected_option["post_func"](result)

                        database.guild_data.update_one(
                            {"_id": ctx.guild.id},
                            {"$set": {selected_option["value"]: result}},
                        )

                        await interact.message.edit(embed=await get_config_embed())

                        await response.reply(
                            embed=create_msg_embed(
                                get_locale_fm(
                                    lang,
                                    "config.successful_change",
                                    name,
                                    response.content,
                                )
                            )
                        )
                    except:
                        await response.reply(
                            embed=create_msg_embed(
                                get_locale_fm(lang, "config.conversion_fail")
                            )
                        )
            except asyncio.TimeoutError:
                await msg_embed(
                    interact.followup, get_locale_fm(lang, "config.no_response", name)
                )
        else:
            # if has options provide an option menu embed
            pass

    edit_button.callback = edit_callback

    clear_button = discord.ui.Button(
        style=discord.ButtonStyle.red, label=get_locale_fm(lang, "button.clear")
    )

    async def clear_callback(interact: discord.Interaction):
        if interact.user.id != ctx.author.id:
            await msg_embed_response(
                interact.response,
                get_locale_fm(lang, "not_your_button"),
                ephemeral=True,
            )
            return

        selected_option = config_options[option_index]
        database.guild_data.update_one(
            {"_id": ctx.guild.id},
            {"$set": {selected_option["value"]: selected_option["default_value"]}},
        )

        await interact.message.edit(embed=await get_config_embed())

        await msg_embed_response(
            interact.response,
            get_locale_fm(
                lang,
                "config.set_default_value",
                get_locale_fm(lang, selected_option["name"]),
                get_locale_fm(lang, str(selected_option["default_value"])),
            ),
        )

    clear_button.callback = clear_callback

    view.add_item(select)
    view.add_item(edit_button)
    view.add_item(clear_button)

    msg = await ctx.send(embed=await get_config_embed(), view=view)


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
