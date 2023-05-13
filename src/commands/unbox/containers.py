"""
Copyright (C) 2022 William Redding - All Rights Reserved

See end of file for licence details
"""

import discord
from discord.ext.commands import Context
from src.util.emojis import CASE_EMOJI, SOUVENIR_PACKAGE_EMOJI, STICKER_CAPSULE_EMOJI
from src.util.images import CASE, SOUVENIR_PACKAGE, STICKER_CAPSULE
from src.util.string_util import currency_str_format
from src.util.embed_func import msg_embed, msg_embed_response
from src.lang.lang import get_locale_fm
from src.util import database

# generate page data, sort by cheapest to most expensive
cases = sorted(
    [
        name
        for name, data in database.containers.items()
        if name != "_id" and data["type"] == "case"
    ],
    key=lambda case: database.containers[case]["price"],
)
souvenir_packages = sorted(
    [
        name
        for name, data in database.containers.items()
        if name != "_id" and data["type"] == "souvenir_package"
    ],
    key=lambda package: database.containers[package]["price"],
)
sticker_capsules = sorted(
    [
        name
        for name, data in database.containers.items()
        if name != "_id" and data["type"] == "sticker_capsule"
    ],
    key=lambda capsule: database.containers[capsule]["price"],
)


# construct page tuples with first element being title and second being the elements on the page
case_pages = [("Cases", cases[i : i + 14]) for i in range(0, len(cases), 14)]
souvenir_package_pages = [
    ("Souvenir Packages", souvenir_packages[i : i + 14])
    for i in range(0, len(souvenir_packages), 14)
]
sticker_capsule_pages = [
    ("Sticker Capsules", sticker_capsules[i : i + 14])
    for i in range(0, len(sticker_capsules), 14)
]

all_pages = case_pages + souvenir_package_pages + sticker_capsule_pages

select_values = [all_pages, case_pages, souvenir_package_pages, sticker_capsule_pages]
select_images = [CASE, CASE, SOUVENIR_PACKAGE, STICKER_CAPSULE]

prev_button = discord.ui.Button(label="◀", style=discord.ButtonStyle.gray)
next_button = discord.ui.Button(label="▶", style=discord.ButtonStyle.gray)


async def containers(ctx: Context, page: int = 1):
    user_data = database.user_data.find_one({"_id": ctx.author.id})

    if user_data is None:
        lang = "en"
    else:
        lang = user_data["lang"]

    if page <= 0 or page > len(all_pages):
        await msg_embed(ctx, get_locale_fm(lang, "invalid_page"))
        return

    page -= 1

    container_page_data = all_pages

    def get_embed(select_value: int = None):
        if select_value is None:
            try:
                select_value = int(select.values[0])
            except IndexError:
                select_value = 0

        container_type, containers = container_page_data[page]

        e = discord.Embed(
            title=get_locale_fm(
                lang,
                "containers.embed.title",
                page + 1,
                len(container_page_data),
                select_labels[select_value],
            ),
            description=get_locale_fm(lang, "containers.embed.description"),
            color=discord.Color.dark_theme(),
        )

        page_field = ""
        for container in containers:
            container_data = database.containers[container]

            page_field += f'• {container_data["formatted_name"]} - **{currency_str_format(container_data["price"])}**\n'
        e.add_field(name=container_type, value=page_field)
        e.set_footer(text=get_locale_fm(lang, "containers.embed.footer"))
        e.set_thumbnail(url=select_images[select_value])
        return e

    # callbacks
    async def prev_callback(interact: discord.Interaction):
        if interact.user.id != ctx.author.id:
            await msg_embed_response(
                interact.response,
                get_locale_fm(lang, "not_your_button"),
                ephemeral=True,
            )
            return

        nonlocal page

        if page > 0:
            page -= 1
        else:
            page = len(container_page_data) - 1
        await interact.response.edit_message(embed=get_embed())

    async def next_callback(interact: discord.Interaction):
        if interact.user.id != ctx.author.id:
            await msg_embed_response(
                interact.response,
                get_locale_fm(lang, "not_your_button"),
                ephemeral=True,
            )
            return

        nonlocal page

        if page < len(container_page_data) - 1:
            page += 1
        else:
            page = 0
        await interact.response.edit_message(embed=get_embed())

    async def select_callback(interact: discord.Interaction):
        if interact.user.id != ctx.author.id:
            await msg_embed_response(
                interact.response,
                get_locale_fm(lang, "not_your_select"),
                ephemeral=True,
            )
            return

        nonlocal container_page_data, page
        select_value = int(select.values[0])
        container_page_data = select_values[select_value]
        page = 0
        await interact.response.edit_message(embed=get_embed(select_value))

    async def view_timeout_callback():
        await msg.delete()

    # create view
    view = discord.ui.View(timeout=30)
    view.on_timeout = view_timeout_callback

    # create select menu
    select = discord.ui.Select(
        options=[
            discord.SelectOption(
                label=get_locale_fm(lang, "containers.select.label.all_containers"),
                value=0,
            ),
            discord.SelectOption(
                label=get_locale_fm(lang, "containers.select.label.cases"),
                value=1,
                emoji=CASE_EMOJI,
            ),
            discord.SelectOption(
                label=get_locale_fm(lang, "containers.select.label.souvenir_packages"),
                value=2,
                emoji=SOUVENIR_PACKAGE_EMOJI,
            ),
            discord.SelectOption(
                label=get_locale_fm(lang, "containers.select.label.sticker_capsules"),
                value=3,
                emoji=STICKER_CAPSULE_EMOJI,
            ),
        ]
    )
    select_labels = [select_option.label for select_option in select.options]
    select.callback = select_callback
    view.add_item(select)

    # create next and previous buttons
    prev_button.callback = prev_callback
    view.add_item(prev_button)

    next_button.callback = next_callback
    view.add_item(next_button)

    msg = await ctx.send(embed=get_embed(), view=view)


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
