import discord
from src.util import database
from src.commands.trading.trade_func import create_item_str
from discord.ext.commands import Context
from src.util.embed_func import msg_embed
from src.lang.lang import get_locale_fm
from src.util.decorators import requires


@requires(users_registered=True)
async def accept(ctx: Context, sender: discord.Member):
    lang = database.user_data.find_one({"_id": ctx.author.id})["lang"]

    with database.mongo_client.start_session() as session:
        with session.start_transaction():
            trade = database.trade_requests.find_one(
                {
                    "_id": sender.id,
                    "recipient_id": ctx.author.id,
                    "send_timestamp": {"$ne": 0},
                },
                session=session,
            )

            if trade is None:
                await msg_embed(
                    ctx, get_locale_fm(lang, "no_incoming_trade", sender.name)
                )
                session.abort_transaction()
                return

            # check items are in both users inventories
            sender_data = database.user_data.find_one({"_id": sender.id})
            recipient_data = database.user_data.find_one({"_id": ctx.author.id})

            sender_items_missing = []
            recipient_items_missing = []

            for item in trade["sender_items"]:
                if item not in sender_data["inventory"]:
                    sender_items_missing.append(item)

            for item in trade["recipient_items"]:
                if item not in recipient_data["inventory"]:
                    recipient_items_missing.append(item)

            if len(sender_items_missing) == 0 and len(recipient_items_missing) == 0:
                # no missing items, next check that the trade will not result in inventory capacity overflow
                if (
                    sender_data["inventory_size"] + len(trade["sender_items"])
                    > sender_data["inventory_capacity"]
                ):
                    e = discord.Embed(
                        title=get_locale_fm(lang, "trade_error"),
                        description=get_locale_fm(
                            lang, "trade_error.author_not_enough_space", sender.name
                        ),
                        color=discord.Color.red(),
                    )
                    await ctx.send(embed=e)
                    return

                if (
                    recipient_data["inventory_size"] + len(trade["recipient_items"])
                    > sender_data["inventory_capacity"]
                ):
                    e = discord.Embed(
                        title=get_locale_fm(lang, "trade_error"),
                        description=get_locale_fm(
                            lang,
                            "trade_error.sender_not_enough_space",
                            sender.name,
                            sender.name,
                        ),
                        color=discord.Color.red(),
                    )
                    await ctx.send(embed=e)
                    return

                # delete trade document - no longer needed
                database.trade_requests.delete_one(
                    {
                        "_id": sender.id,
                        "recipient_id": ctx.author.id,
                        "send_timestamp": {"$ne": 0},
                    },
                    session=session,
                )

                # swap items round
                database.user_data.update_one(
                    {"_id": ctx.author.id},
                    {
                        "$pull": {"inventory": {"$in": trade["recipient_items"]}},
                        "$inc": {"inventory_size" - len(trade["recipient_items"])},
                    },
                    session=session,
                )
                database.user_data.update_one(
                    {"_id": ctx.author.id},
                    {
                        "$push": {"inventory": {"$each": trade["sender_items"]}},
                        "$inc": {"inventory_size": len(trade["sender_items"])},
                    },
                    session=session,
                )
                database.user_data.update_one(
                    {"_id": sender.id},
                    {
                        "$pull": {"inventory": {"$in": trade["sender_items"]}},
                        "$inc": {"inventory_size": -len(trade["sender_items"])},
                    },
                    session=session,
                )
                database.user_data.update_one(
                    {"_id": sender.id},
                    {
                        "$push": {"inventory": {"$each": trade["recipient_items"]}},
                        "$inc": {"inventory_size": len(trade["recipient_items"])},
                    },
                    session=session,
                )

                # send embed to perso n who accepted
                recipient_embed = discord.Embed(
                    title=get_locale_fm(
                        lang, "trade_accept.author_embed.description", sender.name
                    ),
                    color=discord.Color.green(),
                )
                recipient_embed.add_field(
                    name="Your New Items",
                    value=create_item_str(lang, trade["sender_items"]),
                )
                recipient_embed.set_thumbnail(url=ctx.author.display_avatar.url)

                await ctx.send(embed=recipient_embed)

                # inform the original sender that it was accepted
                sender_embed = discord.Embed(
                    title=get_locale_fm(
                        lang, "trade_accept.sender_embed.title", ctx.author.name
                    ),
                    color=discord.Color.green(),
                )
                sender_embed.add_field(
                    name=get_locale_fm(lang, "your_new_items"),
                    value=create_item_str(lang, trade["recipient_items"]),
                )
                recipient_embed.set_thumbnail(url=sender.display_avatar.url)

                await sender.send(embed=sender_embed)

            else:
                # items missing, cancel and inform participants that cannot perform trade!
                database.trade_requests.delete_one(
                    {
                        "_id": sender.id,
                        "recipient_id": ctx.author.id,
                        "send_timestamp": {"$ne": 0},
                    },
                    session=session,
                )

                # send message to recipient
                e = discord.Embed(
                    title=get_locale_fm(lang, "trade_error"),
                    description=get_locale_fm(
                        lang, "trade_error.missing_items", sender.name
                    ),
                    color=discord.Color.red(),
                )
                e.set_thumbnail(url=ctx.author.display_avatar.url)

                e.add_field(
                    name=get_locale_fm(lang, "you_are_missing"),
                    value=create_item_str(lang, recipient_items_missing),
                )
                e.add_field(
                    name=get_locale_fm(lang, "sender_is_missing", sender.name),
                    value=create_item_str(lang, sender_items_missing),
                )

                await ctx.send(embed=e)
