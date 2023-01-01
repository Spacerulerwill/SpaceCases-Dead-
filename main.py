from aiohttp import ClientConnectorError
from discord.ext import commands
from discord.ext.commands import Context

import discord
from os import environ
from src.util import database
from src.util.string_util import get_closest_match
from src.util.constants import PREFIX

cogs = ["user", "help", "unbox", "inventory", "trading"]  

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
    database.init()

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

    #set playing game to cs help
    await bot_instance.change_presence(activity=discord.Game(name=f"{PREFIX}help"))

#handle command errors with error message
@bot_instance.event
async def on_command_error(ctx:Context, error):
    if isinstance(error, commands.CommandNotFound):        
        err_msg, = error.args
        query = err_msg.split('"')[1]
        options = list(bot_instance.all_commands.keys())
        closest_match = get_closest_match(query, options, 0.5)
        if closest_match is None:
            await ctx.send("Command not found!")
        else:
            await ctx.send(f"Command not found! Did you mean `{closest_match}`?")
        return
    raise error

@bot_instance.event
async def on_guild_join(guild: discord.Guild):

    if not guild.system_channel is None and guild.system_channel.permissions_for(guild.me).send_messages:
        channel = guild.system_channel
        print("bruh!")
    else:
        for ch in guild.text_channels:
            if ch.permissions_for(guild.me).send_messages:
                channel = ch
                break
            else:
                return

    e = discord.Embed(
        description=f"""Hello! My name is **{bot_instance.user.name}**

        I am CS:GO gambling and economy bot. With me you can:
        • Unbox your dream skins
        • Trade them with other users
        • Take a risk and upgrade them
        • And more coming soon!

        To setup the bot and start unboxing, ask an **admin** on the sever to the use the command `{PREFIX}setup!`

        Enjoy the bot! - [Spacerulerwill](https://github.com/Spacerulerwill)
        """,
        color=discord.Color.dark_theme()
    )

    e.set_thumbnail(url=bot_instance.user.display_avatar.url)
    await channel.send(embed=e)

def scrape_skin_data():
    from src.scripts.csgostash_scraper import csgostash_scrape
    csgostash_scrape()

def scrape_container_data():
    from src.scripts.container_scraper import scrape_containers
    scrape_containers()
        
if __name__ == "__main__":
    run_bot()