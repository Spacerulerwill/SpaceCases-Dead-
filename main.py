"""
Copyright (C) 2022 William Redding - All Rights Reserved

See end of file for licence details
"""

import discord
import traceback
import asyncio
import datetime
import threading
import time
from os import environ
from src.util import database
from src.lang.lang import get_locale_fm
from src.util.string_util import get_closest_match
from src.util.room_func import delete_room
from src.util.embed_func import msg_embed, welcome_embed
from src.util.constants import PREFIX

from aiohttp import ClientConnectorError
from discord.ext import commands, tasks
from discord.ext.commands import Context

# cogs to load
cogs = ["help", "user", "unbox", "trading", "inventory", "rankings", "games", "config"]

# try read token from text file, if failed read token from server environment variable
try:
    # read local bot_info
    with open("bot_token.txt", "r") as file:
        TOKEN = file.read()

except FileNotFoundError:
    # read token fr om environment variable
    TOKEN = environ["BOT_TOKEN"]

# use all intents
intents = discord.Intents().all()

# instanciate bot with prefix, intents and disabled help command (uses custom command)
bot_instance = commands.Bot(
    command_prefix=[PREFIX, PREFIX.upper(), PREFIX.title()],
    intents=intents,
    help_command=None,
)


# Connect to database, try run using token
def run_bot():
    database.init_collections()
    database.load_data()

    try:
        bot_instance.run(TOKEN)
    except ClientConnectorError:
        print("Failed to connect to discord.py")
        return


# When the bot is ready, load each command cog and start background tasks
@bot_instance.event
async def on_ready():
    print(f"Logged in as: {bot_instance.user.name}")

    # load each cog
    for extension in cogs:
        await bot_instance.load_extension(f"src.cogs.{extension}")
        print(f"Loaded cog: {extension}")

    bot_status_loop.start()
    leaderboard_loop.start()
    threading.Thread(target=generate_skin_data_loop).start()


status_int = 0


def seconds_until(hours, minutes):
    given_time = datetime.time(hours, minutes)
    now = datetime.datetime.now()
    future_exec = datetime.datetime.combine(now, given_time)
    if (
        future_exec - now
    ).days < 0:  # If we are past the execution, it will take place tomorrow
        future_exec = datetime.datetime.combine(
            now + datetime.timedelta(days=1), given_time
        )  # days always >= 0

    return (future_exec - now).total_seconds()


def generate_skin_data_loop():
    while True:
        time.sleep(seconds_until(0, 0))
        database.scrape_container_data()
        database.scrape_skin_data()
        time.sleep(
            60
        )  # Practical solution to ensure that the func isn't spammed as long as it is 00:00


# loop that cycles the bot status every 10 seconds
@tasks.loop(seconds=10)
async def bot_status_loop():
    global status_int

    match status_int:
        case 0:
            await bot_instance.change_presence(
                activity=discord.Game(name=f"{PREFIX}help | {PREFIX}info")
            )
        case 1:
            await bot_instance.change_presence(
                activity=discord.Game(
                    name=f"{database.user_data.count_documents({})} users | {len(bot_instance.guilds)} servers"
                )
            )

    status_int = (status_int + 1) % 2


# loop that updates the leaderboard every hour
@tasks.loop(hours=1)
async def leaderboard_loop():
    database.get_leaderboard(bot_instance)


# handle command errors with an appriopriate error messages
@bot_instance.event
async def on_command_error(ctx: Context, error):
    user_data = database.user_data.find_one({"_id": ctx.author.id})

    if user_data is None:
        lang = "en"
    else:
        lang = user_data["lang"]

    if isinstance(error, commands.CommandNotFound):
        (err_msg,) = error.args
        query = err_msg.split('"')[1]
        options = list(bot_instance.all_commands.keys())

        closest_match = get_closest_match(query, options, 0.5)
        if closest_match is None:
            await msg_embed(ctx, get_locale_fm(lang, "command_not_found"))
        else:
            await msg_embed(
                ctx, get_locale_fm(lang, "command_not_found_suggest", closest_match)
            )
        return

    elif isinstance(error, commands.BadArgument):
        (err_msg,) = error.args

        query = err_msg.split('"')

        try:
            desired_type = get_locale_fm(lang, query[1])

        except KeyError:
            # if could not find type, its a user not found
            await msg_embed(ctx, get_locale_fm(lang, "command_error.no_user"))
            return

        param_name = query[3].replace("_", " ")

        await msg_embed(
            ctx,
            get_locale_fm(
                lang, "command_error.incorrect_type", param_name, desired_type
            ),
        )
        return

    elif isinstance(error, commands.MissingRequiredArgument):
        param_name = error.param.name.replace("_", " ")
        await msg_embed(
            ctx,
            get_locale_fm(lang, "command_error.missing_required_argument", param_name),
        )
        return

    elif isinstance(error, commands.BadLiteralArgument):
        param_name = error.param.name.replace("_", "/")
        await msg_embed(
            ctx, get_locale_fm(lang, "command_error.invalid_option", param_name)
        )
        return

    elif isinstance(error, commands.MissingPermissions):
        await msg_embed(
            ctx,
            get_locale_fm(
                lang,
                "command_error.missing_permissions",
                ", ".join(error.missing_permissions),
            ),
        )
        return

    elif isinstance(error, commands.CommandOnCooldown):
        await msg_embed(
            ctx, get_locale_fm(lang, "command_error.cooldown", error.retry_after)
        )
        return

    else:
        tb = traceback.format_exception(type(error), error, error.__traceback__)
        string = "".join(tb)
        e = discord.Embed(
            title="Oops! Something went wrong!",
            description="This has been automatically reported to the development team. It will be fixed soon!",
            color=discord.Color.red(),
        )
        await ctx.send(embed=e)
        raise error


# send welcome message on joining a server
@bot_instance.event
async def on_guild_join(guild: discord.Guild):
    # try system channel, otherwise loop through all otherchannels to find one
    if (
        not guild.system_channel is None
        and guild.system_channel.permissions_for(guild.me).send_messages
    ):
        channel = guild.system_channel
        await channel.send(embed=welcome_embed("en", bot_instance))
    else:
        for ch in guild.text_channels:
            if ch.permissions_for(guild.me).send_messages:
                channel = ch
                await channel.send(embed=welcome_embed("en", bot_instance))
                break


@bot_instance.event
async def on_message(message: discord.Message):
    # if message sent from a room, cancel the room deletion task for it and restart it
    room_data = database.rooms.get(message.author.id)

    if room_data is not None:
        room = room_data[0]
        task = room_data[1]
        task.cancel()
        room_data[1] = asyncio.create_task(delete_room(message.author.id, room))

    # process commands as usua l - lower case message before sending to make case insensitive
    message.content = message.content.lower()
    await bot_instance.process_commands(message)


if __name__ == "__main__":
    database.init_collections()
    database.refresh_game_data()

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
