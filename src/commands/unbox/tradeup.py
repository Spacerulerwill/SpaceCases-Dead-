import discord
from discord.ext.commands import Context
from src.util.embed_func import msg_embed, msg_embed_response
from src.util.constants import (
    trade_up_rarity_dict,
    case_wear_ranges_lower,
    conditions,
    rarity_color_dict,
)
from src.util.decorators import requires
from src.lang.lang import get_locale_fm, get_locale
from src.util.string_util import currency_str_format
from src.util import database
from PIL import Image
import requests
import random
from io import BytesIO
from PIL import ImageFont
from PIL import ImageDraw
from datetime import datetime
from collections import Counter

big_font = ImageFont.truetype("res/font/Roboto-Bold.ttf", 12)
small_font = ImageFont.truetype("res/font/Roboto-Bold.ttf", 8)
blue = (50, 75, 117)
RAND_LOWER = 10**11
RAND_UPPER = (10**12) - 1


@requires(users_registered=True)
async def tradeup(ctx: Context, *args):
    user_data = database.user_data.find_one({"_id": ctx.author.id})
    inventory = user_data["inventory"]
    lang = user_data["lang"]

    if len(args) != len(set(args)):
        await msg_embed(ctx, get_locale(lang, "tradeup.error.same_item_twice"))
        return

    if len(args) != 10:
        await msg_embed(ctx, get_locale(lang, "tradeup.error.not_enough_items"))
        return

    item_data = [
        database.skin_data["skins"][inventory[int(item_index) - 1]["name"]]
        for item_index in args
    ]

    # check all items exist
    if any(int(x) > len(inventory) for x in args):
        await msg_embed(ctx, get_locale(lang, "tradeup.error.not_all_found"))
        return

    # check they are all of same rarity
    rarities = [data["rarity"] for data in item_data]
    if any(rarity != rarities[0] for rarity in rarities):
        await msg_embed(ctx, get_locale(lang, "tradeup.error.not_same_rarity"))
        return

    rarity = rarities[0]  # safe to do as we ensured they all have the same rarity

    # check they are not a mix of stattrak and non stattak
    is_stattraks = ["StatTrak" in data["formatted_name"] for data in item_data]
    if any(x != is_stattraks[0] for x in is_stattraks):
        await msg_embed(ctx, get_locale(lang, "tradeup.error.stattrak_mix"))
        return

    is_stattrak = is_stattraks[
        0
    ]  # safe to do as we ensured they are all either stattrak or not stattrak

    # check if any are not trade uppable
    if any(not data["can_tradeup"] for data in item_data):
        await msg_embed(ctx, get_locale(lang, "tradeup.error.invalid_items"))
        return

    skin_names = [data["no_wear_formatted_name"] for data in item_data]
    skin_collections = [data["container"] for data in item_data]

    contract_signed = False

    async def cancel_contract():
        if not contract_signed:
            nonlocal e
            e.set_footer(text="")
            await msg.edit(embed=e, view=None)

    async def sign_callback(interact: discord.Interaction):
        if interact.user.id != ctx.author.id:
            await msg_embed_response(
                interact.response,
                get_locale_fm(lang, "not_your_button"),
                ephemeral=True,
            )
            return

        nonlocal contract_signed

        # ordered list of tuples of each collection to their respective chance
        col_prob = list(Counter(skin_collections).most_common())

        final_probability_dict = {}
        collections = [x[0] for x in col_prob]
        probs = [x[1] for x in col_prob]

        for count, col in enumerate(collections):
            final_probability_dict[col] = sum(probs[0:count]) / 10

        # pick random container
        container_rand = random.random()
        for key, value in final_probability_dict.items():
            if container_rand > value:
                container = key
                break

        container_data = database.cases_and_collections[container]
        new_skin_rarity = trade_up_rarity_dict[rarity]
        new_item = random.choice(container_data["items"][new_skin_rarity])
        item_data = database.skin_data["no_wear_skins"][new_item]

        # pick a random skin from the rarity above - linear interpolation
        final_float = (
            sum([inventory[int(item_index) - 1]["float"] for item_index in args])
            / 10
            * (item_data["max_float"] - item_data["min_float"])
            + item_data["min_float"]
        )

        for wear, upper in case_wear_ranges_lower.items():
            if final_float > upper:
                condition = conditions[wear].lower() + " "
                break

        new_item = condition + new_item

        if is_stattrak:
            new_item = "stattrak " + new_item

        new_item_data = database.skin_data["skins"][new_item]

        # change embed and resend
        contract_signed = True
        e = discord.Embed(
            title=new_item_data["formatted_name"],
            color=rarity_color_dict[new_skin_rarity],
            description=get_locale_fm(
                lang, "inspect_in_3d", new_item_data["inspect_url"]
            ),
        )
        e.title = new_item_data["formatted_name"]
        e.color = rarity_color_dict[new_skin_rarity]
        e.description = get_locale_fm(
            lang, "inspect_in_3d", new_item_data["inspect_url"]
        )

        e.add_field(
            name=get_locale_fm(lang, "market_value"),
            value=currency_str_format(new_item_data["price"]),
        )
        e.add_field(
            name=get_locale_fm(lang, "rarity"), value=get_locale_fm(lang, rarity)
        )
        e.add_field(name=get_locale_fm(lang, "float"), value=str(final_float))
        e.set_thumbnail(url=new_item_data["image_url"])
        e.set_image(url="attachment://contract1.png")
        e.set_footer(text="")

        await interact.response.edit_message(embed=e, view=None)

    # create trade up contract image
    date = datetime.strftime(datetime.now(), "%A, %b %d, %Y")

    form_number = random.randint(RAND_LOWER, RAND_UPPER)

    response = requests.get(
        "https://static.wikia.nocookie.net/cswikia/images/a/a3/Csgo_contrect.png/revision/latest?cb=20180507174532"
    )
    img = Image.open(BytesIO(response.content))
    draw = ImageDraw.Draw(img)
    draw.text((470, 20), date, blue, font=big_font)  # date
    draw.text((127, 55), str(form_number), blue, font=big_font)  # form number
    draw.text((100, 135), "10", blue, font=big_font)  # numbers of items
    draw.text((330, 135), "???????", blue, font=big_font)
    draw.text((40, 80), ctx.author.name, blue, font=big_font)  # name

    for i in range(4):
        draw.text((45, 195 + (i * 13)), skin_names[i], blue, font=small_font)

    for i in range(4):
        draw.text((168, 195 + (i * 13)), skin_names[i + 4], blue, font=small_font)

    for i in range(2):
        draw.text((315, 195 + (i * 13)), skin_names[i + 8], blue, font=small_font)

    async def cancel_callback(interact: discord.Interaction):
        if interact.user.id != ctx.author.id:
            await msg_embed_response(
                interact.response,
                get_locale_fm(lang, "not_your_button"),
                ephemeral=True,
            )
            return

        await interact.response.defer()
        await cancel_contract()

    # create view and buttons
    view = discord.ui.View(timeout=30)
    view.on_timeout = cancel_contract

    cancel = discord.ui.Button(
        label=get_locale(lang, "button.cancel"), style=discord.ButtonStyle.red
    )
    sign = discord.ui.Button(
        label=get_locale(lang, "button.sign"), style=discord.ButtonStyle.green
    )
    sign.callback = sign_callback
    cancel.callback = cancel_callback

    view.add_item(cancel)
    view.add_item(sign)

    with BytesIO() as image_binary:
        img.save(image_binary, "PNG")
        image_binary.seek(0)
        e = discord.Embed()
        file = discord.File(fp=image_binary, filename="contract1.png")
        e.set_image(url="attachment://contract1.png")
        e.set_footer(text=get_locale(lang, "tradeup.footer"))
        msg = await ctx.send(file=file, embed=e, view=view)
