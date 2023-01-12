from aiohttp import ClientConnectorError
from discord.ext import commands, tasks
from discord.ext.commands import Context

import discord
import asyncio
from os import environ
from src.util import database
from src.util.string_util import get_closest_match
from src.util.embed_func import msg_embed, welcome_embed
from src.util.constants import PREFIX, ROOM_DELETION_TIME

cogs = ["user", "help", "unbox", "inventory", "trading", "config"]  

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

#start the bots
def run_bot():
    global bot_instance
    
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

    #set playing game to cs help
    await bot_instance.change_presence(activity=discord.Game(name=f"{PREFIX}help"))

    bot_status_loop.start()

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
    raise error

@bot_instance.event
async def on_guild_join(guild: discord.Guild):

    if not guild.system_channel is None and guild.system_channel.permissions_for(guild.me).send_messages:
        channel = guild.system_channel
    else:
        for ch in guild.text_channels:
            if ch.permissions_for(guild.me).send_messages:
                channel = ch
                break

    await channel.send(embed=welcome_embed(bot_instance))

async def delete_room(owner_id:int, thread:discord.Thread):
    await asyncio.sleep(ROOM_DELETION_TIME)
    await thread.delete()
    database.rooms.pop(owner_id, None)

@bot_instance.event
async def on_message(message:discord.Message):

    room_data = database.rooms.get(message.author.id)

    if room_data is not None:
        room = room_data[0]
        task = room_data[1]

        if message.channel:
            task.cancel()
            task = asyncio.create_task(delete_room(message.author.id, room))

    await bot_instance.process_commands(message)

def scrape_skin_data():
    from src.scripts.csgostash_scraper import csgostash_scrape
    csgostash_scrape()

def scrape_container_data():
    from src.scripts.container_scraper import scrape_containers
    scrape_containers()
        
if __name__ == "__main__":
    run_bot()