import discord
from src.util import database
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
                
                database.trade_requests.delete_one({"_id": sender.id, "recipient-id": ctx.author.id, "send-timestamp": {"$ne": 0}}, session=session)

            else:
                # items missing, cannot perform trade!
                pass

            print(sender_items_missing, recipient_items_missing)