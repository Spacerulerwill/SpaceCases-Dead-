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

from PIL import Image
import requests
from io import BytesIO


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
    async def balance(self, ctx: Context, member: Optional[discord.Member]):
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

    @commands.command()
    async def test(self, ctx: Context):
        response = requests.get(
            "https://steamcommunity-a.akamaihd.net/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpou6ryFAR17P7YJgJE6d2kq4iOluHtDLfQhGxUppR3iLvHpNygigfiqkVpYWunJYSSJAc7YFHZ_QS4k-ft1pPvvZzOzSd9-n51g3wi1hY/512fx384f"
        )
        img = Image.open(BytesIO(response.content))

        response = requests.get(
            "https://steamcommunity-a.akamaihd.net/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXQ9QVcJY8gulRcQFXICOis2s3XUmJ8KghYibakOQBlnfaZJmUTtd7lx4Hax_Gmau6IxzMFupEj3OiZpt6l0VLg_0FrYGD2dtSLMlhpp4buLJ0/260fx260f"
        )
        img2 = Image.open(BytesIO(response.content)).resize((60, 60))

        for x in range(2):
            for y in range(2):
                img.paste(
                    img2, (x * img2.width, img.height - img2.height - (y * img2.height))
                )

        with BytesIO() as image_binary:
            img.save(image_binary, "PNG")
            image_binary.seek(0)
            e = discord.Embed()
            file = discord.File(fp=image_binary, filename="image.png")
            e.set_image(url="attachment://image.png")
            await ctx.send(file=file, embed=e)


# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(User(bot))
