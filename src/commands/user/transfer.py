import discord
from discord.ext.commands import Context
from src.util import database
from src.util.format import currency_str_format
from decimal import Decimal
from pymongo import ReturnDocument

async def transfer(self, ctx:Context, member: discord.Member, amount:float):
    if member is ctx.author:
        await ctx.send("You cannot transfer money to yourself!")
        return

    if amount <= 0:
        await ctx.send("Amount to transfer must be greater than 0")
        return

    #convert amount to cents
    amount = int(Decimal(amount) * 100)

    #start a session to multi docuemnt atomic transaction
    with database.mongo_client.start_session() as session:
        with session.start_transaction():
            post_doc = database.user_data.find_one_and_update({"_id": ctx.author.id}, 
            [{
            "$set": {                  
                'balance': {
                    "$cond": {
                        "if": {
                            "$gte": ["$balance", amount]
                        },
                        "then": {
                            "$subtract": ["$balance", amount],
                        },
                        "else": "$balance"
                    }
                },
                "modified": {
                    "$cond": {
                        "if": {
                            "$gte": ["$balance", amount]
                        },
                        "then": True,
                        
                        "else": False
                    }
                }
            }
            }], session=session, return_document=ReturnDocument.AFTER)

            if post_doc["modified"]:
                database.user_data.find_one_and_update({"_id":member.id}, {"$inc": {"balance": amount}}, session=session)
                await ctx.send(f"Successfully transferred {currency_str_format(amount)} to {member.name}'s account")
            else:
                await ctx.send("You have insufficient funds!")