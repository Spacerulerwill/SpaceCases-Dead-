#import all neccesary modules
from aiohttp import ClientConnectorError
from discord.ext import commands

import discord
from os import environ
from src.util import database
from src.util.constants import PREFIX

cogs = ["unbox", "user", "help",  "minigame", "rankings", "shop"]  

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
bot_instance = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None) #define command decorator

def run_bot():
    global bot_instance
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

    #set playing game to !helpcs open csgo weapon case
    await bot_instance.change_presence(activity=discord.Game(name=f"{PREFIX}help"))
        
if __name__ == "__main__":
    database.init()
    run_bot()