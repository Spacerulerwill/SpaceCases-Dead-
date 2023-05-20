"""
Copyright (C) 2022 William Redding - All Rights Reserved

See end of file for licence details
"""

import discord
import logging
import traceback
import asyncio
import datetime
import threading
import time
import os
from dotenv import load_dotenv
from src.util import database
from src.lang.lang import get_locale_fm
from src.util.string_util import get_closest_match
from src.util.room_func import delete_room, Room
from src.util.embed_func import msg_embed, welcome_embed
from src.util.constants import PREFIX

from aiohttp import ClientConnectorError
from discord.ext import commands, tasks
from discord.ext.commands import Context

# load environment variables
load_dotenv(".env")

# detemrine whether on debug or production
environment: str = os.getenv("ENV")

match environment:
    case "DEBUG":
        log_level = logging.DEBUG
    case "PROD":
        log_level = logging.INFO
    case _:
        raise ValueError(
            f"Environment variable ENV must be DEBUG or PROD, not {environment}"
        )

logfile_loc = datetime.datetime.utcnow().strftime(
    f"logs/%Y_%m_%d_%H_%M_%S_{environment}.log"
)

# setup logging
logging.basicConfig(
    level=log_level,
    format="%(levelname)s (%(asctime)s): %(message)s",
    datefmt="%I:%M:%S %p",
    filename=logfile_loc,
    filemode="w+",
)

# cogs to load
cogs = ["help", "user", "unbox", "trading", "inventory", "rankings", "games", "config"]

# use all intents
intents = discord.Intents().all()

# instancia  bot with prefix, intents and disabled help command (uses custom command)
bot_instance = commands.Bot(
    command_prefix=[PREFIX, PREFIX.upper(), PREFIX.title()],
    intents=intents,
    help_command=None,
)


# Connect to database, try run using token
def run_bot():
    database.init_collections()
    database.load_game_data()

    TOKEN: str = os.getenv("BOT_TOKEN")

    try:
        bot_instance.run(TOKEN)
    except ClientConnectorError:
        logging.critical("Failed to connect to discord.py... Aborting!")
        return


# When the bot is ready, load each command cog and start background tasks
@bot_instance.event
async def on_ready():
    logging.info(f"Logged in as {bot_instance.user.name}")

    # load each cog
    for extension in cogs:
        await bot_instance.load_extension(f"src.cogs.{extension}")
        logging.info(f"Loaded cog: {extension}")

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
        database.refresh_game_data()
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
    room: Room = database.rooms.get(message.author.id)

    if room is not None:
        room.task.cancel()
        room.task = asyncio.create_task(delete_room(message.author.id, room.thread))

    # process commands as usua l - lower case message before sending to make case insensitive
    message.content = message.content.lower()
    await bot_instance.process_commands(message)


if __name__ == "__main__":
    run_bot()

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
