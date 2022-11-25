# this cog is for commands that affect the user's details and profile
# Commands:
# * register
# * claim
# * balance

import discord
from discord.ext import commands
from discord.ext.commands import Context
from src.util.constants import PREFIX

#commands
from src.commands.user.register import register
from src.commands.user.claim import claim
from src.commands.user.balance import balance
from src.commands.user.transfer import transfer

# initialise class
class User(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    #register for a bank account
    @commands.command(description="Register for a bank account", usage=f"""
    `{PREFIX}register`
    """)
    async def register(self, ctx:Context):
        await register(ctx)

    #claim daily allowance of money
    @commands.command(description="Claim money every 12 hours", usage=f"""
    `{PREFIX}claim`
    """)
    async def claim(self, ctx:Context):
        await claim(ctx)

    #check user balance
    @commands.command(description="Check a user's balance", usage=f"""
    `{PREFIX}balance <user>`
    **Arguments**
    `<user>` - optional - user to check balance of
    """)
    async def balance(self, ctx: Context, member: discord.Member = None):
        await balance(ctx, member)

    @balance.error
    async def balance_error(self, ctx:Context, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Incorrect Arguments!")

    #send user money
    @commands.command(description="Transfer money to another user", usage=f"""
    `{PREFIX}transfer <user> <amount>`
    **Arguments**
    `<user>` - user to transfer money to
    `<amount>` - the amount of money to transfer
    """)
    async def transfer(self, ctx:Context, member: discord.Member, amount:float):
        await transfer(ctx, member, amount)

    @transfer.error
    async def transfer_error(self, ctx:Context, error):
        if isinstance(error, commands.MissingRequiredArgument):
            error:commands.MissingRequiredArgument
            if error.param.name == "member":
                await ctx.send("Oops! You forget to supply a recipient user")
            if error.param.name == "amount":
                await ctx.send("Oops! You forget to supply an amount of money")
        elif isinstance(error, commands.BadArgument): 
            print("Incorrect Arguments!")
                
# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(User(bot))