import discord
from src.util import database
from src.lang.lang import get_locale_fm
from src.util.constants import case_wear_ranges_lower, case_wear_ranges_upper
from src.util.string_util import round_sig_fig
from src.util.embed_func import msg_embed, msg_embed_response
from src.util.decorators import requires
from discord.ext.commands import Context
import random


@requires(users_registered=True)
async def upgrade(ctx: Context, item_index: int, *args):
    result_item_name = " ".join(args[:]).strip().lower()

    user_data = database.user_data.find_one({"_id": ctx.author.id})
    lang = user_data["lang"]

    if item_index > len(user_data["inventory"]):
        await msg_embed(ctx, get_locale_fm(lang, "inventory.not_at_index", item_index))
        return

    item_index -= 1
    start_item_name = user_data["inventory"][item_index]["name"]
    start_item_float = user_data["inventory"][item_index]["float"]

    start_item_data = database.skin_data["skins"][start_item_name]

    try:
        result_item_data = database.skin_data["skins"][result_item_name]
    except KeyError:
        await msg_embed(
            ctx, get_locale_fm(lang, "inventory.not_found_name", result_item_name)
        )
        return

    if result_item_data["price"] <= start_item_data["price"]:
        await msg_embed(ctx, get_locale_fm(lang, "upgrade.cant_upgrade_to_cheaper"))
        return

    price_multiplier = result_item_data["price"] / start_item_data["price"]
    percentage_chance = 1 / price_multiplier
    has_upgraded = False

    e = discord.Embed(
        description=get_locale_fm(
            lang,
            "upgrade.embed.title",
            start_item_data["formatted_name"],
            result_item_data["formatted_name"],
        )
    )
    e.add_field(
        name=get_locale_fm(lang, "price_multiplier"),
        value=f"{round_sig_fig(price_multiplier, 2)}X",
    )
    e.add_field(
        name=get_locale_fm(lang, "chance"),
        value=f"{round_sig_fig(percentage_chance*100, 2)}%",
    )
    e.set_thumbnail(url=start_item_data["image_url"])
    e.set_image(url=result_item_data["image_url"])
    e.set_footer(
        icon_url=ctx.author.display_avatar.url,
        text=get_locale_fm(lang, "upgrade.embed.footer"),
    )

    async def on_view_timeout():
        if not has_upgraded:
            await msg.delete()

    async def upgrade_callback(interact: discord.Interaction):
        nonlocal has_upgraded, e

        if interact.user.id != ctx.author.id:
            await msg_embed_response(
                interact.response,
                get_locale_fm(lang, "not_your_button"),
                ephemeral=True,
            )
            return

        if random.random() < percentage_chance:
            # upgrade successful - replace item
            # start a session to multi docuemnt atomic transaction
            with database.mongo_client.start_session() as session:
                with session.start_transaction():
                    update_result = database.user_data.update_one(
                        {"_id": ctx.author.id},
                        {
                            "$pull": {
                                "inventory": {
                                    "name": start_item_name,
                                    "float": start_item_float,
                                }
                            },
                        },
                        session=session,
                    )

                    # failed to pull - item no longer exists abort transaction
                    if update_result.modified_count == 0:
                        e = discord.Embed(
                            title=get_locale_fm(lang, "upgrade.error.title"),
                            description=get_locale_fm(
                                lang,
                                "upgrade.error.item_missing",
                                start_item_data["formatted_name"],
                            ),
                        )
                        e.set_thumbnail(url=ctx.author.display_avatar.url)
                        session.abort_transaction()
                    else:
                        # successful at pull, push new item with a new random float
                        worst_condition_float = case_wear_ranges_upper[
                            result_item_data["condition_index"]
                        ]

                        if result_item_data["max_float"] < worst_condition_float:
                            worst_condition_float = result_item_data["max_float"]

                        best_condition_float = case_wear_ranges_lower[
                            result_item_data["condition_index"]
                        ]

                        if result_item_data["min_float"] > best_condition_float:
                            best_condition_float = result_item_data["min_float"]

                        upgraded_item_float = random.uniform(
                            worst_condition_float, best_condition_float
                        )

                        database.user_data.update_one(
                            {"_id": ctx.author.id},
                            {
                                "$push": {
                                    "inventory": {
                                        "name": result_item_name,
                                        "float": upgraded_item_float,
                                    }
                                }
                            },
                            session=session,
                        )
                        e.color = discord.Color.green()
                        e.set_footer(text=None)
        else:
            # upgrade not successful - remove item
            # start a session to multi docuemnt atomic transaction
            with database.mongo_client.start_session() as session:
                with session.start_transaction():
                    update_result = database.user_data.update_one(
                        {"_id": ctx.author.id},
                        {
                            "$pull": {
                                "inventory": {
                                    "name": start_item_name,
                                    "float": start_item_float,
                                }
                            },
                        },
                        session=session,
                    )

                    # failed to pull - item no longer exists abort transaction
                    if update_result.modified_count == 0:
                        e = discord.Embed(
                            title=get_locale_fm(lang, "upgrade.error.title"),
                            description=get_locale_fm(
                                lang,
                                "upgrade.error.item_missing",
                                result_item_data["formatted_name"],
                            ),
                        )
                        e.set_thumbnail(url=ctx.author.display_avatar.url)
                        session.abort_transaction()
                    else:
                        # successful at pull, decrement inventory size
                        database.user_data.update_one(
                            {"_id": ctx.author.id},
                            {"$inc": {"inventory_size": -1}},
                            session=session,
                        )
                        e.color = discord.Color.red()
                        e.set_footer(text=None)

        has_upgraded = True
        await msg.edit(embed=e, view=None)

    view = discord.ui.View(timeout=30)
    view.on_timeout = on_view_timeout

    upgrade_button = discord.ui.Button(
        label=get_locale_fm(lang, "button.upgrade"), style=discord.ButtonStyle.green
    )
    upgrade_button.callback = upgrade_callback
    view.add_item(upgrade_button)

    msg = await ctx.send(embed=e, view=view)
