"""
Copyright (C) 2022 William Redding - All Rights Reserved

Commands
~~~~~~~~
* register
* claim
* balance
* transfer
* lang
* room

See end of file for licence details
"""

import random
import discord
from discord.ext import commands
from discord.ext.commands import Context
from discord.ext.commands.bot import Bot
from src.util import database

from typing import Literal, Optional
from decimal import Decimal

from PIL import Image
import requests
from io import BytesIO
from PIL import ImageFont
from PIL import ImageDraw

from timeit import default_timer as timer
from datetime import timedelta

# commands
from src.commands.user.register import register
from src.commands.user.claim import claim
from src.commands.user.balance import balance
from src.commands.user.transfer import transfer
from src.commands.user.room import room
from src.commands.user.lang import lang


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
        font = ImageFont.truetype("res/font/Roboto-Bold.ttf", 20)

        skin_name = "factory new mp7 abyssal apparition"
        float = random.random()

        skin_data = database.skin_data["items "][skin_name]
        start = timer()
        skin_img_url = skin_data["image_url"]
        sticker_urls = [
            "https://steamcommunity-a.akamaihd.net/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXQ9QVcJY8gulRcQFXICOis2s3XUmJ8KghYibakOQBlnfaZJmUTtd7lx4Hax_Gmau6IxzMFupEj3OiZpt6l0VLg_0FrYGD2dtSLMlhpp4buLJ0/260fx260f"
        ] * 4

        response = requests.get(skin_img_url)
        skin = Image.open(BytesIO(response.content))
        draw = ImageDraw.Draw(skin)

        # draw text
        draw.text((0, 0), skin_data["formatted_name"], (255, 255, 255), font=font)
        draw.text((0, 30), str(float), (255, 255, 255), font=font)

        # draw stickers
        for count, sticker_url in enumerate(sticker_urls):
            response = requests.get(sticker_url)
            sticker_img = Image.open(BytesIO(response.content)).resize((60, 60))
            skin.paste(
                sticker_img,
                (
                    (count % 2) * sticker_img.width,
                    skin.height
                    - sticker_img.height
                    - ((count // 2) * sticker_img.height),
                ),
            )

        with BytesIO() as image_binary:
            skin.save(image_binary, "PNG")
            image_binary.seek(0)
            e = discord.Embed()
            file = discord.File(fp=image_binary, filename="image.png")
            e.set_image(url="attachment://image.png")
            await ctx.send(file=file, embed=e)

        end = timer()
        print(f"Executed in {timedelta(seconds=end-start)}")


# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot: Bot):
    await bot.add_cog(User(bot))


"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
