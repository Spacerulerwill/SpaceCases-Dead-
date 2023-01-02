import discord
from src.util import database
from src.commands.trading.trade_func import create_item_str
from discord.ext.commands import Context

@requires(users_registered=True)
async def accept(ctx:Context, sender:discord.Member):
    with database.mongo_client.start_session() as session:
        with session.start_transaction():
            trade = database.trade_requests.find_one({"_id": sender.id, "recipient-id": ctx.author.id, "send-timestamp": {"$ne": 0}}, session=session)
            
            if trade is None:
                await ctx.send(f"You do not have an incoming trade from {sender.name}")
                session.abort_transaction()
                return
            
            # check items are in both users inventories
            sender_data = database.user_data.find_one({"_id": sender.id})
            recipient_data = database.user_data.find_one({"_id": ctx.author.id})

            sender_items_missing = []
            recipient_items_missing = []

            for item in trade["sender-items"]:
                if item not in sender_data["inventory"]:
                    sender_items_missing.append(item)
                
            for item in trade["recipient-items"]:
                if item not in recipient_data["inventory"]:
                    recipient_items_missing.append(item)

            if len(sender_items_missing) == 0 and len(recipient_items_missing) == 0:
                # no missing items, next check that the trade will not result in inventory capacity overflow

                if sender_data["inventory-size"] + len(trade["sender-items"]) > sender_data["inventory-capacity"]:
                    trade_continue = False

                if recipient_data["inventory-size"] + len(trade["recipient-items"]) > sender_data["inventory-capacity"]:
                    trade_continue = False

                if not trade_continue:
                    return

                database.trade_requests.delete_one({"_id": sender.id, "recipient-id": ctx.author.id, "send-timestamp": {"$ne": 0}}, session=session)

                # swap items round
                database.user_data.update_one(
                    {"_id": ctx.author.id},
                    {
                        "$pull": {
                            "inventory": {
                                "$in": trade["recipient-items"]
                            }
                        },
                        "$inc": {
                            "inventory-size" -len(trade["recipient-items"])
                        },                   
                    },
                    session=session  
                )
                database.user_data.update_one(
                    {"_id": ctx.author.id},
                    {
                        "$push": {
                            "inventory": { "$each": trade["sender-items"]}
                        },
                        "$inc": {
                            "inventory-size": len(trade["sender-items"])
                        }
                    },
                    session=session  
                ) 
                database.user_data.update_one(
                    {"_id": sender.id},
                    {
                        "$pull": {
                            "inventory": {
                                "$in": trade["sender-items"]
                            }
                        },
                        "$inc": {
                            "inventory-size": -len(trade["sender-items"])
                        }
                    }, 
                    session=session  
                )
                database.user_data.update_one(
                    {"_id": sender.id},
                    {
                        "$push": {
                            "inventory": { "$each": trade["recipient-items"]}
                        },
                        "$inc": {
                            "inventory-size": len(trade["recipient-items"])
                        }
                    },
                    session=session   
                )

                #send embed person who accepted
                recipient_embed = discord.Embed(
                    title=f"Trade from {sender.name} accepted!",
                    color=discord.Color.green()
                )
                recipient_embed.add_field(name="Your New Items", value=create_item_str(trade["sender-items"]))
                recipient_embed.set_thumbnail(url=ctx.author.display_avatar.url)

                await ctx.send(embed=recipient_embed)

                sender_embed = discord.Embed(
                    title=f"{ctx.author.name} accepted your trade request!",
                    color=discord.Color.green()
                )
                sender_embed.add_field(name="Your New Items", value=create_item_str(trade["recipient-items"]))
                recipient_embed.set_thumbnail(url=sender.display_avatar.url)

                await sender.send(embed=sender_embed)
                
            else:
                # items missing, cancel and inform participants that cnanot perform trade!
                database.trade_requests.delete_one({"_id": sender.id, "recipient-id": ctx.author.id, "send-timestamp": {"$ne": 0}}, session=session)

                # send message to recipient
                e = discord.Embed(
                    title="Trade Error",
                    description=f"The trade from {sender.name} could not take place and has been cancelled as items were missing from one or both participants inventories.",
                    color=discord.Color.red()
                )
                e.set_thumbnail(url=ctx.author.display_avatar.url)

                e.add_field(name="You Are Missing", value=create_item_str(recipient_items_missing))
                e.add_field(name=f"{sender.name} is Missing", value=create_item_str(sender_items_missing))

                await ctx.send(embed=e)

                # only send to the sender if they have items missing
                if len(sender_items_missing) != 0:
                    # send message to sender
                    e = discord.Embed(
                        title="Trade Error",
                        description=f"Your trade to {ctx.author.name} could not take place and has been cancelled as items were missing from one or both participants inventories",
                        color=discord.Color.red()
                    )

                    e.set_thumbnail(url=sender.display_avatar.url)

                    e.add_field(name=f"{ctx.author.name} is Missing", value=create_item_str(recipient_items_missing))
                    e.add_field(name="You Are Missing", value=create_item_str(sender_items_missing))

                    await sender.send(embed=e)
