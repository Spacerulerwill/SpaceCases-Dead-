"""
Copyright (C) 2023 William Redding - All Rights Reserved

See end of file for licence details
"""

from discord.ext.commands import Context
from src.util import database
from src.lang.lang import get_locale_fm
from src.util.embed_func import msg_embed
from src.util.decorators import requires
from src.util.room_func import delete_room, get_guild_room_create_channel
import discord
import asyncio


@requires(users_registered=True)
async def room(ctx: Context, public_private: str):
    lang = database.user_data.find_one({"_id": ctx.author.id})["lang"]

    try:
        guild_data = database.guild_data.find_one({"_id": ctx.guild.id})
    except AttributeError:
        # if there is no ctx.guild ( i.e. in a dm )
        await msg_embed(ctx, get_locale_fm(lang, "room.cannot_create_here"))
        return

    room_creation_channel = get_guild_room_create_channel(ctx.guild, guild_data)
    if (
        guild_data is None
        or guild_data["unbox_room_creation_channel_id"] is None
        or room_creation_channel is None
    ):
        await msg_embed(ctx, get_locale_fm(lang, "room.not_setup"))
        return

    if ctx.channel.id != guild_data["unbox_room_creation_channel_id"]:
        await msg_embed(
            ctx,
            get_locale_fm(lang, "room.not_in_channel", room_creation_channel.mention),
        )
        return

    room = database.rooms.get(ctx.author.id)
    if room is not None:
        # if room is in a different guild, delete room but don't cancel auto deletion task - we want the old room to still delete itself after 15 minutes
        if ctx.guild.id != room[0].guild.id:
            database.rooms.pop(ctx.author.id, None)
        else:
            await msg_embed(ctx, get_locale_fm(lang, "room.exists", room[0].mention))
            return

    if public_private == "public":
        thread_type = discord.ChannelType.public_thread
    else:
        thread_type = discord.ChannelType.private_thread

    thread: discord.Thread = await ctx.channel.create_thread(
        name=f"{ctx.author.name}'s room", type=thread_type
    )

    if public_private == "private":
        await msg_embed(ctx, get_locale_fm(lang, "room.private_created"))

    await msg_embed(thread, get_locale_fm(lang, "room.greeting", ctx.author.mention))
    await thread.add_user(ctx.author)

    task = asyncio.create_task(delete_room(ctx.author.id, thread))
    database.rooms[ctx.author.id] = [thread, task]


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
