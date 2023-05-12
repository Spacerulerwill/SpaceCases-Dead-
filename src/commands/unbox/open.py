import discord
import random
from discord.ext.commands import Context
from src.util import database
from src.lang.lang import get_locale_fm
from src.util.decorators import requires
from src.util.constants import KEY_PRICE, rarity_color_dict
from src.util.string_util import (
    currency_str_format,
    get_closest_match,
    get_inspect_link_3D,
)
from src.util.item_func import gen_item, get_item_embed
from src.util.embed_func import msg_embed, msg_embed_response


@requires(room=True, users_registered=True)
async def open(ctx: Context, *args):
    container_name = " ".join(args[:]).strip().lower()

    user_data = database.user_data.find_one({"_id": ctx.author.id})
    lang = user_data["lang"]

    # check case exists
    try:
        container_data = database.containers[container_name]
        container_price = container_data["price"]

        # souvenir packages dont require keys
        if container_data["type"] != "souvenir_package":
            container_price += KEY_PRICE

    except KeyError:
        # try and find closest match
        closest_match = get_closest_match(container_name, database.containers.keys())

        # if match is reasonably close enough
        if closest_match is None:
            await msg_embed(ctx, get_locale_fm(lang, "container.not_found"))
        else:
            container_data = database.containers[closest_match]
            await msg_embed(
                ctx,
                get_locale_fm(lang, "container.not_found_suggest", closest_match),
            )
        return

    # check user has enough balance for case
    if user_data["balance"] < container_price:
        await msg_embed(ctx, get_locale_fm(lang, "not_enough_funds"))
        return

    # select skin rarity
    rarity_rand = random.random()
    case_odds: dict = container_data["odds"]
    for key, value in case_odds.items():
        if rarity_rand > value:
            rarity = key
            break

    skin_pool = container_data["items"][rarity]
    chosen_item = random.choice(skin_pool)

    # get the item dict
    item = gen_item(chosen_item, container_data["type"])

    item_data = database.skin_data["skins"][item["name"]]
    e = get_item_embed(lang, item_data)

    # if its a weapon, add float field
    if container_data["type"] in ["case", "souvenir_package"]:
        e.add_field(name=get_locale_fm(lang, "float"), value=str(item["float"]))

    e.set_footer(text=get_locale_fm(lang, "open.embed.footer"))

    interacted_with = False

    # decrement balance, increment total spent, increase total return and containers opened
    database.user_data.update_one(
        {"_id": ctx.author.id},
        {
            "$inc": {
                "balance": -(container_price),
                "stats.total_spent": container_price,
                "stats.total_return": item_data["price"],
                "stats.containers_opened": 1,
            }
        },
    )

    # callbacks
    async def sell_item():
        # change color to dark gray, remove footer, change balance to have balance of skin
        database.user_data.update_one(
            {"_id": ctx.author.id}, {"$inc": {"balance": item_data["price"]}}
        )

        e.colour = discord.colour.Color.dark_gray()
        e.set_footer(text="")

        await msg.edit(embed=e, view=None)

    async def sell_callback(interact: discord.Interaction):
        if ctx.author.id != interact.user.id:
            await msg_embed_response(
                interact.response,
                get_locale_fm(lang, "not_your_button"),
                ephemeral=True,
            )
            return

        nonlocal interacted_with

        if not interacted_with:
            interacted_with = True
            await sell_item()
        else:
            await interact.response.defer()

    async def inventory_callback(interact: discord.Interaction):
        if ctx.author.id != interact.user.id:
            await msg_embed_response(
                interact.response,
                get_locale_fm(lang, "not_your_button"),
                ephemeral=True,
            )
            return

        nonlocal interacted_with

        if not interacted_with:
            # add to user inventory
            filter_ = {
                "_id": ctx.author.id,
                "$expr": {"$lt": ["$inventory_size", "$inventory_max_capacity"]},
            }
            update = {
                "$push": {"inventory": item},
                "$inc": {"inventory_size": 1},
            }

            update_result = database.user_data.update_one(filter_, update)

            if update_result.modified_count == 1:
                interacted_with = True
                e.colour = discord.colour.Color.green()
                e.set_footer(text="")
                await msg.edit(embed=e, view=None)

            elif update_result.modified_count == 0:
                await msg_embed_response(
                    interact.response, get_locale_fm(lang, "inventory.full")
                )
        else:
            await interact.response.defer()

    # if not interacted with after 30 seconds, sell the item
    async def view_timeout_callback():
        nonlocal interacted_with
        if not interacted_with:
            interacted_with = True
            await sell_item()

    # create buttons
    view = discord.ui.View(timeout=30)
    view.on_timeout = view_timeout_callback
    inventory_button = discord.ui.Button(
        label=get_locale_fm(lang, "button.add_to_inventory"),
        style=discord.ButtonStyle.green,
    )
    inventory_button.callback = inventory_callback
    sell_button = discord.ui.Button(
        label=get_locale_fm(lang, "button.sell"), style=discord.ButtonStyle.red
    )
    sell_button.callback = sell_callback
    view.add_item(inventory_button)
    view.add_item(sell_button)

    # send embed
    msg = await ctx.send(embed=e, view=view)