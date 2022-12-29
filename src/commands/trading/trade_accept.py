import discord
from src.util import database
from src.commands.trading.trade_func import create_item_str
from discord.ext.commands import Context

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
                # no missing items, all good to trade!
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
                    },
                    session=session  
                )
                database.user_data.update_one(
                    {"_id": ctx.author.id},
                    {
                        "$push": {
                            "inventory": { "$each": trade["sender-items"]}
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
                    }, 
                    session=session  
                )
                database.user_data.update_one(
                    {"_id": sender.id},
                    {
                        "$push": {
                            "inventory": { "$each": trade["recipient-items"]}
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
                # items missing, cannot perform trade!
                e = discord.Embed(
                    title="Trade Error",
                    description=f"The trade to {sender.name} could not take place as items were missing from one or both participants inventories. Try again once you have these items, or decline the request.",
                    color=discord.Color.red()
                )
                e.add_field()
                e.set_thumbnail(url=ctx.author.display_avatar.url)

                e.add_field(name="You Are Missing", value=create_item_str(recipient_items_missing))
                e.add_field(name=f"{sender.name} is Missing", value=create_item_str(sender_items_missing))

                await ctx.send(embed=e)