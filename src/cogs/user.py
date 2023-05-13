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
import ffmpy
import discord
from discord.ext import commands
from discord.ext.commands import Context

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
from PIL import ImageFont
from PIL import ImageDraw

from timeit import default_timer as timer
from datetime import timedelta

from src.util import database


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

        skin_data = database.skin_data["skins"][skin_name]
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

    @commands.command()
    async def test2(self, ctx: Context):
        ff = ffmpy.FFmpeg(inputs={"cash.mp4": None}, outputs={"cash.gif": None})

        ff.run()

        e = discord.Embed(title="bru")
        e.set_image(
            url="https://cdn.csgoskins.gg/public/videos/floats/v1/embedding/ursus-knife-rust-coat.webm"
        )
        await ctx.send(embed=e)


# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(User(bot))


"""
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.

                            Preamble

  The GNU General Public License is a free, copyleft license for
software and other kinds of works.

  The licenses for most software and other practical works are designed
to take away your freedom to share and change the works.  By contrast,
the GNU General Public License is intended to guarantee your freedom to
share and change all versions of a program--to make sure it remains free
software for all its users.  We, the Free Software Foundation, use the
GNU General Public License for most of our software; it applies also to
any other work released this way by its authors.  You can apply it to
your programs, too.

  When we speak of free software, we are referring to freedom, not
price.  Our General Public Licenses are designed to make sure that you
have the freedom to distribute copies of free software (and charge for
them if you wish), that you receive source code or can get it if you
want it, that you can change the software or use pieces of it in new
free programs, and that you know you can do these things.

  To protect your rights, we need to prevent others from denying you
these rights or asking you to surrender the rights.  Therefore, you have
certain responsibilities if you distribute copies of the software, or if
you modify it: responsibilities to respect the freedom of others.

  For example, if you distribute copies of such a program, whether
gratis or for a fee, you must pass on to the recipients the same
freedoms that you received.  You must make sure that they, too, receive
or can get the source code.  And you must show them these terms so they
know their rights.

  Developers that use the GNU GPL protect your rights with two steps:
(1) assert copyright on the software, and (2) offer you this License
giving you legal permission to copy, distribute and/or modify it.

  For the developers' and authors' protection, the GPL clearly explains
that there is no warranty for this free software.  For both users' and
authors' sake, the GPL requires that modified versions be marked as
changed, so that their problems will not be attributed erroneously to
authors of previous versions.

  Some devices are designed to deny users access to install or run
modified versions of the software inside them, although the manufacturer
can do so.  This is fundamentally incompatible with the aim of
protecting users' freedom to change the software.  The systematic
pattern of such abuse occurs in the area of products for individuals to
use, which is precisely where it is most unacceptable.  Therefore, we
have designed this version of the GPL to prohibit the practice for those
products.  If such problems arise substantially in other domains, we
stand ready to extend this provision to those domains in future versions
of the GPL, as needed to protect the freedom of users.

  Finally, every program is threatened constantly by software patents.
States should not allow patents to restrict development and use of
software on general-purpose computers, but in those that do, we wish to
avoid the special danger that patents applied to a free program could
make it effectively proprietary.  To prevent this, the GPL assures that
patents cannot be used to render the program non-free.

  The precise terms and conditions for copying, distribution and
modification follow.
"""
