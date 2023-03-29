import discord
import asyncio
from os import environ
from src.util import database, lang
from src.util.lang import get_locale
from src.util.string_util import get_closest_match
from src.util.room_func import delete_room
from src.util.embed_func import msg_embed, welcome_embed
from src.util.constants import PREFIX, err_msg_type_dict

from aiohttp import ClientConnectorError
from discord.ext import commands, tasks
from discord.ext.commands import Context

# cogs to load
cogs = ["help", "user", "unbox", "trading", "inventory", "rankings", "games", "config"]  

#try read token from text file, if failed read token from server environment variable
try:
    #read local bot_info
    with open("bot_token.txt", "r") as file:
        TOKEN = file.read()
        
except FileNotFoundError:
    #read token from environment variable
    TOKEN = environ["BOT_TOKEN"]

#use all intents
intents = discord.Intents().all()

#instanciate bot with prefix, intents and disabled help command (uses custom command) 
bot_instance = commands.Bot(command_prefix=[PREFIX, PREFIX.upper(), PREFIX.title()], intents=intents, help_command=None) #define command decorator

# Connect to database, try run using token
def run_bot():  
    database.init_collections()
    database.load_data()
    lang.init()

    try:
        bot_instance.run(TOKEN)
    except ClientConnectorError: 
        print("Failed to connect to discord.py")
        return

# When the bot is ready, load each command cog and start background tasks  
@bot_instance.event
async def on_ready():
    print(f'Logged in as: {bot_instance.user.name}')
  
    #load each cog
    for extension in cogs:
        await bot_instance.load_extension(f'src.cogs.{extension}')
        print(f"Loaded cog: {extension}")

    bot_status_loop.start()
    leaderboard_loop.start()

status_int = 0

# loop that cycles the bot status every 10 seconds
@tasks.loop(seconds=10)
async def bot_status_loop():
    global status_int
    
    match status_int:
        case 0:
            await bot_instance.change_presence(activity=discord.Game(name=f"{PREFIX}help | {PREFIX}info"))
        case 1:
            await bot_instance.change_presence(activity=discord.Game(name=f"{database.user_data.count_documents({})} users | {len(bot_instance.guilds)} servers"))

    status_int = (status_int + 1) % 2

# loop that updates the leaderboard every hour
@tasks.loop(hours=1)
async def leaderboard_loop():
    database.get_leaderboard()

#handle command errors with an appriopriate error messages
@bot_instance.event
async def on_command_error(ctx:Context, error):
    lang = database.user_data.find_one({"_id": ctx.author.id})["lang"]

    if isinstance(error, commands.CommandNotFound):        
        err_msg, = error.args
        query = err_msg.split('"')[1]
        options = list(bot_instance.all_commands.keys())

        closest_match = get_closest_match(query, options, 0.5)
        if closest_match is None:
            await msg_embed(ctx, get_locale(lang, "command_not_found"))
        else:
            await msg_embed(ctx, get_locale(lang, "command_not_found_suggest", closest_match))
        return

    if isinstance(error, commands.BadArgument):
        err_msg, = error.args

        query = err_msg.split('"')

        try:
            desired_type = err_msg_type_dict[query[1]]
        except KeyError:
            # if could not find type, its a user not found
            await msg_embed(ctx, get_locale(lang, "command_error.no_user"))
            return

        param_name = query[3].replace("_", " ")

        await msg_embed(ctx, get_locale(lang, "command_error.incorrect_type", param_name, desired_type))
        return

    if isinstance(error, commands.MissingRequiredArgument):
        param_name = error.param.name.replace("_", " ")
        await msg_embed(ctx, get_locale(lang, "command_error.missing_required_argument", param_name))
        return

    if isinstance(error, commands.BadLiteralArgument):
        param_name = error.param.name.replace("_", "/")
        await msg_embed(ctx, get_locale(lang, "command_error.invalid_option", param_name))
        return

    if isinstance(error, commands.MissingPermissions):
        await msg_embed(ctx, get_locale(lang, "command_error.missing_permissions", ', '.join(error.missing_permissions)))
        return

    if isinstance(error, commands.CommandOnCooldown):
        await msg_embed(ctx, get_locale(lang, "command_error.cooldown", round(error.retry_after, 2)))
        return

    raise error

#send welcome message on joining a server
@bot_instance.event
async def on_guild_join(guild: discord.Guild):
    #try system channel, otherwise loop through all otherchannels to find one
    if not guild.system_channel is None and guild.system_channel.permissions_for(guild.me).send_messages:
        channel = guild.system_channel
        await channel.send(embed=welcome_embed("en", bot_instance))
    else:
        for ch in guild.text_channels:
            if ch.permissions_for(guild.me).send_messages:
                channel = ch
                await channel.send(embed=welcome_embed("en", bot_instance))
                break

@bot_instance.event
async def on_message(message:discord.Message):
    # if message sent from a room, cancel the room deletion task for it and restart it
    room_data = database.rooms.get(message.author.id)

    if room_data is not None:
        room = room_data[0]
        task = room_data[1]
        task.cancel()
        room_data[1] = asyncio.create_task(delete_room(message.author.id, room))

    # process commands as usual - lower case message before sending
    message.content = message.content.lower()
    await bot_instance.process_commands(message)

def scrape_skin_data():
    from src.scripts.csgostash_scraper import csgostash_scrape
    database.init_collections()
    csgostash_scrape()

def scrape_container_data():
    from src.scripts.container_scraper import scrape_containers
    database.init_collections()
    scrape_containers()
        
if __name__ == "__main__":
    run_bot()