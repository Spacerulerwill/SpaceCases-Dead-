"""
User Command Cog
~~~~~~~~~~~~~~~~~~~

This cog contains the commands:
* Register
* Claim
* Balance
* Transfer
* Stats
* Room
"""

import discord
from discord.ext import commands
from discord.ext.commands import Context
from src.util.constants import PREFIX

#commands
from src.commands.user.register import register
from src.commands.user.claim import claim
from src.commands.user.balance import balance
from src.commands.user.transfer import transfer
from src.commands.user.stats import stats
from src.commands.user.room import room

from typing import Literal, Optional

# initialise class
class User(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    #register for a bank account
    @commands.command(description="Register for a bank account", usage=
    {
        "Syntax": f"`{PREFIX}register`"
    })
    async def register(self, ctx:Context):
        await register(ctx)

    #claim daily allowance of money
    @commands.command(description="Claim daily allowance", usage=
    {
        "Syntax": f"`{PREFIX}claim`"
    })
    async def claim(self, ctx:Context):
        await claim(ctx)

    #check user balance
    @commands.command(description="Check a user's balance", usage=
    {
        "Syntax": f"`{PREFIX}balance <user>`",
        "Arguments": "`<user>` - user to check balance of - optional"
    }, aliases=["bal"])
    async def balance(self, ctx: Context, member:discord.Member = None):
        await balance(ctx, member)

    #send user money
    @commands.command(description="Transfer money to another user", usage=
    {
        "Syntax": f"`{PREFIX}transfer <user> <amount>`",
        "Arguments": """
        `<user>` - user to transfer money to
        `<amount>` - the amount of money to transfer in dollars
        """
    })
    async def transfer(self, ctx:Context, member: discord.Member, amount:float):
        await transfer(ctx, member, amount)

    @commands.command(description="Check a user's statistics", usage=
    {
        "Syntax": f"`{PREFIX}stats <user>`",
        "Arguments": "`<user>` - user to check stats of - optional"
    })
    async def stats(self, ctx:Context, member:discord.Member=None):
        await stats(ctx, member)       

    
    @commands.command(description="Create a room for unboxing items", usage={
        "Syntax": f"`{PREFIX}room public/private`",
        "Arguments": "`public/private - whether room is public or private thread - optional",
    })
    async def room(self, ctx:Context, public_private:Literal["public", "private"]="public"):
        await room(ctx, public_private)

# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(User(bot))