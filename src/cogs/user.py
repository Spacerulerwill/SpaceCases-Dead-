"""
User Command Cog
~~~~~~~~~~~~~~~~~~~

This cog contains the commands:
* Register
* Claim
* Balance
* Transfer
* Lang
* Room
"""

import discord
from discord.ext import commands
from discord.ext.commands import Context
from src.lang.lang import supported_languages, get_locale_fm
from src.util.constants import PREFIX

# commands
from src.commands.user.register import register
from src.commands.user.claim import claim
from src.commands.user.balance import balance
from src.commands.user.transfer import transfer
from src.commands.user.room import room
from src.commands.user.lang import lang

from typing import Literal, Optional
from decimal import Decimal


# initialise class
class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # register for a bank account
    @commands.command()
    async def register(self, ctx: Context):
        await register(ctx)

    # claim daily allowance of money
    @commands.command()
    async def claim(self, ctx: Context):
        await claim(ctx)

    # check user balance
    @commands.command(aliases=["bal"])
    async def balance(self, ctx: Context, member:Optional[discord.Member]):
        await balance(ctx, member)

    # send user money
    @commands.command()
    async def transfer(self, ctx: Context, member: discord.Member, amount: Decimal):
        await transfer(ctx, member, amount)

    @commands.command()
    async def room(
        self, ctx: Context, room_type: Literal["public", "private"] = "public"
    ):
        await room(ctx, room_type)

    @commands.command()
    async def lang(self, ctx: Context, language: str = None):
        await lang(ctx, language)


# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(User(bot))
