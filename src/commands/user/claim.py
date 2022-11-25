from discord.ext.commands import Context
from src.util import database
from src.util.constants import TWELVE_HOURS, PREFIX
from pymongo import ReturnDocument
from datetime import datetime
import time

async def claim(ctx:Context):
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

    if post_doc == None:
        await ctx.send(f"You are not registered! Use `{PREFIX}register` to register")
        return
    
    #if document modified
    if post_doc["modified"]:
        await ctx.send("You have claimed $100! You can claim again in 12 hours")

    else:
        time_left_seconds = TWELVE_HOURS - (int(time.time()) - post_doc["last-claim"])
        date_time = datetime.fromtimestamp( time_left_seconds )  
        time_left_formatted = date_time.strftime("%H:%M:%S")
        await ctx.send(f"You have already claimed! You can claim again in {time_left_formatted}")