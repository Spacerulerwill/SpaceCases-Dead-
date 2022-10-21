# this cog is for commands that affect the user's details and profile
# Commands:
# * register
# * claim
# * balance

import discord
from discord.ext import commands
from src.util import database
from src.util.constants import PREFIX
from datetime import timezone, datetime
from decimal import Decimal

# initialise class
class UserCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #register a profile
    @commands.command()
    async def register(self, ctx):
        if database.user_data.find_one({"_id": ctx.author.id}) == None:
            profile = {
                "_id": ctx.author.id,
                "balance": '0.0',
                "last-claim": "01/01/1970",
                "inventory": [],
                "inventory-size": 5,
                "inventory-value": '0.0',
                "containers-opened": 0,
                "total-spent": '0.0',
                "total-return": '0.0',
            }

            database.user_data.insert_one(profile)
            await ctx.send(f"Registered! Use {PREFIX}profile to see your profile")
        else:
            await ctx.send("You are already registered!")

    @commands.command()
    async def claim(self, ctx):

        #check if user is registed
        user = database.user_data.find_one({"_id": ctx.author.id})

        if user == None:
            await ctx.send(f"You aren't registed! Use {PREFIX}register to register")
            return

        #if user is registed
        #get last claim time
        last_claim = user['last-claim']
        
        #convert to date time
        dt = datetime.strptime(last_claim ,"%d/%m/%Y")
        dt = dt.strftime("%d/%m/%Y")
        
        #get current time
        now = datetime.now(tz=timezone.utc)
        dmy = now.strftime("%d/%m/%Y")

        #see if it has been atleast a day
        if dmy != dt:
            #add money
            current_balance = Decimal(user['balance'])
            
            database.user_data.update_one({"_id":ctx.author.id},{"$set" :{"balance" : str(current_balance+100)}})

            #update last claim date
            database.user_data.update_one({"_id":ctx.author.id},{"$set" :{"last-claim" : str(dmy)}})

            await ctx.send("You claimed $100! Come back tomorrow to claim again")
        else:
            await ctx.send("You must wait until tomorrow to claim again!")

    @commands.command()
    async def balance(self, ctx, member: discord.Member = None):
        #if used an @ to specify a member
        if member == None:
            member = ctx.author
            name = "Your"
        else:
            name = f"{member.display_name}'s"
            
        #get user
        user = database.user_data.find_one({"_id": member.id})

        if user == None:
            if member == ctx.author:
                await ctx.send(f"You are not registered! Use {PREFIX}register to register")
            else:
                await ctx.send(f'{member.display_name} has not registered yet')
        else:
            user_balance = Decimal(user["balance"])
            await ctx.send(f"{name} balance is: ${'{:.2f}'.format(user_balance)}")

    @commands.command()
    async def profile(self, ctx):
        user = database.user_data.find_one({"_id": ctx.author.id})

        if user == None:
            await ctx.send(f"You are not registered! Use {PREFIX}register to register")
            return

        try:
            percent_return = round(float(user["total-return"]) / float(user["total-spent"]) * 100)
        except ZeroDivisionError:
            percent_return = 0.0

        stats  = f"""
        Containers Opened: {user["containers-opened"]}
        Total Spent: {user["total-spent"]}
        Total Return: {user["total-return"]}
        % Return: {percent_return}%
        """
        
        e = discord.Embed(title=f"{ctx.author.name}'s profile")
        e.add_field(name="Statistics", value=stats)
        e.set_thumbnail(url=ctx.message.author.avatar.url)
        await ctx.send(embed=e)

# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(UserCommands(bot))