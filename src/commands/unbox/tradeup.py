import discord
from discord.ext.commands import Context
from PIL import Image
import requests
import random
from io import BytesIO
from PIL import ImageFont
from PIL import ImageDraw 
from datetime import datetime

big_font = ImageFont.truetype("res/font/Roboto-Bold.ttf", 12)
small_font = ImageFont.truetype("res/font/Roboto-Bold.ttf", 8)
blue = (50, 75, 117)
RAND_LOWER = 10**11
RAND_UPPER = (10**12)-1

async def tradeup(ctx:Context):
    
    # create trade up contract image
    date = datetime.strftime(datetime.now(), "%A, %b %d, %Y")

    form_number = random.randint(RAND_LOWER, RAND_UPPER)
    skins = ["AWP | Dragon Lore"] * 10

    response = requests.get(
        "https://static.wikia.nocookie.net/cswikia/images/a/a3/Csgo_contrect.png/revision/latest?cb=20180507174532"
    )
    img = Image.open(BytesIO(response.content))
    draw = ImageDraw.Draw(img)
    draw.text((470, 20),date,blue,font=big_font) # date
    draw.text((127, 55), str(form_number),blue,font=big_font) #form number
    draw.text((100, 135), "10", blue, font=big_font) # numbers of items
    draw.text((330, 135), "???????",blue, font=big_font)
    draw.text((40, 80), ctx.author.name, blue, font=big_font) # name

    for i in range(4):
        draw.text((45,195 + (i*13)), skins[i], blue, font=small_font)

    for i in range(4):
        draw.text((168,195 + (i*13)), skins[i+4], blue, font=small_font)

    for i in range(2):
        draw.text((315,195 + (i*13)), skins[i+8], blue, font=small_font)

    with BytesIO() as image_binary:
        img.save(image_binary, "PNG")
        image_binary.seek(0)
        e = discord.Embed()
        file = discord.File(fp=image_binary, filename="image.png")
        e.set_image(url="attachment://image.png")
        await ctx.send(file=file, embed=e)