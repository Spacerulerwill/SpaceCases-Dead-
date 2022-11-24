# this cog is for commands that affect the user's details and profile
# Commands:
# * register
# * claim
# * balance

import discord
from discord.ext import commands
from discord.ext.commands import Context
from src.util import database
from src.util.constants import PREFIX, TWELVE_HOURS, DEFAULT_INVENTORY_SIZE
from src.util.format import currency_str_format
from datetime import datetime
from pymongo.collection import ReturnDocument
import time
from decimal import Decimal

# initialise class
class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #register a profile
    @commands.command(description="Register for a bank account", usage=f"""
    `{PREFIX}register`
    """)
    async def register(self, ctx:Context):
        if database.user_data.find_one({"_id": ctx.author.id}) == None:
            database.user_data.insert_one({
                "_id": ctx.author.id,
                "balance": 0,
                "last-claim": 0,
                "inventory": [None for i in range(DEFAULT_INVENTORY_SIZE)],
                "inventory-size": 5,
                "containers-opened": 0,
                "total-spent": 0,
                "total-return": 0,
                "modified": False
            })
            await ctx.send(f"Registered! Use `{PREFIX}claim` to claim some money!")
        else:
            await ctx.send("You are already registered!")

    #claim daily allowance of money
    @commands.command(description="Claim money every 12 hours", usage=f"""
    `{PREFIX}claim`
    """)
    async def claim(self, ctx:Context):
        #update balance and set last claim to now if been twelve hours since last claim
        post_doc = database.user_data.find_one_and_update({"_id": ctx.author.id},
        [
            {
                "$set": {                  
                    'balance': {
                        "$cond": {
                            "if": {
                                "$gte": [int(time.time()) - TWELVE_HOURS, '$last-claim']
                            },
                            "then": {
                                "$add": ["$balance",10000],
                            },
                            "else": "$balance"
                        }
                    },

                    'last-claim': {
                        "$cond": {
                            "if": {
                                "$gte": [int(time.time()) - TWELVE_HOURS, '$last-claim']
                            },
                            "then": int(time.time()),
                            
                            "else": "$last-claim"
                        }
                    },

                    "modified": {
                        "$cond": {
                            "if": {
                                "$gte": [int(time.time()) - TWELVE_HOURS, '$last-claim']
                            },
                            "then": True,
                            
                            "else": False
                        }
                    }
                },
            }
        ], return_document=ReturnDocument.AFTER)
        
        #if document modified
        if post_doc["modified"]:
            await ctx.send("You have claimed $100! You can claim again in 12 hours")

        else:
            time_left_seconds = TWELVE_HOURS - (int(time.time()) - post_doc["last-claim"])
            date_time = datetime.fromtimestamp( time_left_seconds )  
            time_left_formatted = date_time.strftime("%H:%M:%S")
            await ctx.send(f"You have already claimed! You can claim again in {time_left_formatted}")

    @commands.command(description="Check a user's balance", usage=f"""
    `{PREFIX}balance <user>`
    **Arguments**
    `<user>` - optional - user to check balance of
    """)
    async def balance(self, ctx: Context, member: discord.Member = None):
        if member is None:
            member = ctx.author

        user_data:dict = database.user_data.find_one({"_id": member.id})

        if user_data is not None: 
            await ctx.send(f"{member.name}'s balance is: {currency_str_format(user_data['balance'])}")
        else:
            await ctx.send(f"{member.name} is not registered!")

    @commands.command(description="Transfer money to another user", usage=f"""
    `{PREFIX}transfer <user> <amount>`
    **Arguments**
    `<user>` - user to transfer money too
    `<amount>` - the amount of money to transfer
    """)
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
                
# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(User(bot))