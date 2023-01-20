import discord
import asyncio
from os import environ
from src.util import database
from src.util.string_util import get_closest_match
from src.util.embed_func import msg_embed, welcome_embed
from src.util.constants import PREFIX, ROOM_DELETION_TIME, err_msg_type_dict

from aiohttp import ClientConnectorError
from discord.ext import commands, tasks
from discord.ext.commands import Context

# cogs to load
cogs = ["help", "user", "unbox", "trading", "inventory", "rankings", "config"]  

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

#start the bot
def run_bot():    
    database.init()

    try:
        bot_instance.run(TOKEN) #run the client using using my bot's token
    except ClientConnectorError: 
        print("Failed to connect to discord.py")
        
@bot_instance.event
async def on_ready():
    #print login message
    print(f'Logged in as: {bot_instance.user.name}')
  
    #load each cog
    for extension in cogs:
        await bot_instance.load_extension(f'src.cogs.{extension}')
        print(f"Loaded cog: {extension}")

    bot_status_loop.start()
    leaderboard_loop.start()

# task to run every 10 seconds - cycle bot status inbetween values
status_int = 0
@tasks.loop(seconds=10)
async def bot_status_loop():
    global status_int
    
    match status_int:
        case 0:
            await bot_instance.change_presence(activity=discord.Game(name=f"{PREFIX}help | {PREFIX}info"))
        case 1:
            await bot_instance.change_presence(activity=discord.Game(name=f"{database.user_data.count_documents({})} users | {len(bot_instance.guilds)} servers"))

    status_int = (status_int + 1) % 2

@tasks.loop(hours=1)
async def leaderboard_loop():
    database.get_leaderboard()

#handle command errors with error message
@bot_instance.event
async def on_command_error(ctx:Context, error):

    if isinstance(error, commands.CommandNotFound):        
        err_msg, = error.args
        query = err_msg.split('"')[1]
        options = list(bot_instance.all_commands.keys())

        closest_match = get_closest_match(query, options, 0.5)
        if closest_match is None:
            await msg_embed(ctx, "Command not found!")
        else:
            await msg_embed(ctx, f"Command not found! Did you mean `{closest_match}`?")
        return

    if isinstance(error, commands.BadArgument):
        err_msg, = error.args
        print(query)

        try:
            desired_type = err_msg_type_dict[query[1]]
        except KeyError:
            # if could not find type, its a user not found
            await msg_embed(ctx, "**Error!** Could not find user!")
            return

        param_name = query[3].replace("_", " ")
        await msg_embed(ctx, f"**Error!** Argument `{param_name}` must be {desired_type}")
        return

    if isinstance(error, commands.MissingRequiredArgument):
        await msg_embed(ctx, f"**Oops!** You forgot to supply the argument: `{error.param.name}`")
        return

    if isinstance(error, commands.BadLiteralArgument):
        param_name = error.param.name.replace("_", "/")
        await msg_embed(ctx, f"**Error!** Argument must be one of the following options: `{param_name}`")
        return

    if isinstance(error, commands.MissingPermissions):
        await msg_embed(ctx, f"**Error!** You are missing the following permissions to use this command: `{', '.join(error.missing_permissions)}`")
        return

    raise error

@bot_instance.event
async def on_guild_join(guild: discord.Guild):

    # first try welcome channel, if can't just find the first available text channel.
    if not guild.system_channel is None and guild.system_channel.permissions_for(guild.me).send_messages:
        channel = guild.system_channel
        await channel.send(embed=welcome_embed(bot_instance))
    else:
        for ch in guild.text_channels:
            if ch.permissions_for(guild.me).send_messages:
                channel = ch
                await channel.send(embed=welcome_embed(bot_instance))
                break

# task to delete room after time
async def delete_room(owner_id:int, thread:discord.Thread):
    await asyncio.sleep(ROOM_DELETION_TIME)
    await thread.delete()
    database.rooms.pop(owner_id, None)

@bot_instance.event
async def on_message(message:discord.Message):

    # if message sent from a room, cancel the room deletion task for it and restart it
    room_data = database.rooms.get(message.author.id)

    if room_data is not None:
        room = room_data[0]
        task = room_data[1]

        if message.channel:
            task.cancel()
            task = asyncio.create_task(delete_room(message.author.id, room))

    # process commands as usual
    await bot_instance.process_commands(message)

def scrape_skin_data():
    from src.scripts.csgostash_scraper import csgostash_scrape
    csgostash_scrape()

def scrape_container_data():
    from src.scripts.container_scraper import scrape_containers
    scrape_containers()
        
if __name__ == "__main__":
    run_bot()