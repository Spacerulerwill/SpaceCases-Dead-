from discord.ext.commands import Context
from src.util import database
from src.util.format import currency_str_format
from src.util.skin_func import gen_item
from src.util.constants import TWELVE_HOURS, PREFIX, case_wear_ranges_lower, conditions, rarity_color_dict
from pymongo import ReturnDocument
from datetime import datetime
import discord
import time
import random

CLAIM_MONEY_AMOUNTS = [
    5000,
    7500,
    10000,
    10000,
    12000,
    14000,
    16000,
    18000,
    20000,
    20000,
    22500,
    25000,
    27500,
    30000
]

CLAIM_BONUS_REWARDS = {
    4: "classified",
    10: "covert",
    14: "rare items"
}

async def claim(ctx:Context):
    #update balance and set last claim to now if been twelve hours since last claim
    post_doc = database.user_data.find_one_and_update({"_id": ctx.author.id},
    [   
        {
            "$set": {              
                'balance': {
                    "$cond": {
                        "if": {
                            "$gte": ["$claim-streak", 14]
                        },
                        "then": {
                            "$add": ["$balance", 30000]
                        },
                        "else": {
                            "$let": {
                                "vars": {
                                    "claim_money_amounts": CLAIM_MONEY_AMOUNTS
                                },
                                "in": {
                                    "$cond": {
                                        "if": {
                                            "$gte": [int(time.time()) - TWELVE_HOURS, '$last-claim']
                                        },
                                        "then": {
                                            "$add": ["$balance", {"$arrayElemAt": ["$$claim_money_amounts", "$claim-streak"]}]
                                        },
                                        "else": "$balance"
                                    }
                                }
                            }, 
                        }
                    }
                },

                #'last-claim': {
                #    "$cond": {
                #        "if": {
                #            "$gte": [int(time.time()) - TWELVE_HOURS, '$last-claim']
                #        },
                #        "then": int(time.time()),
                #        
                ##        "else": "$last-claim"
                #    }
                #},

                'claim-streak': {
                    "$cond": {
                        "if": {
                            "$gte": [int(time.time()) - TWELVE_HOURS, '$last-claim']
                        },
                        "then": {
                            "$add": ["$claim-streak", 1]
                        },
                        "else": "$claim-streak"
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

        #create embed
        e = discord.Embed(title="You have successfully claimed your daily reward!", description="You can claim again in 12 hours", color=discord.Color.green())
        e.set_thumbnail(url=ctx.author.avatar.url)
        e.set_footer(text="Note: Streaks reset 24 hours after your last claim")

        view = None

        prev_streak = post_doc["claim-streak"]-1

        if post_doc["claim-streak"] >= 14: 
            e.add_field(name="Amount:", value="$300.00", inline=True)
        else:      
            e.add_field(name="Amount:", value=currency_str_format(CLAIM_MONEY_AMOUNTS[prev_streak]), inline=True)

        e.add_field(name="New Balance:", value=currency_str_format(post_doc["balance"]), inline=True)
        e.add_field(name="Streak 🔥", value=post_doc["claim-streak"], inline=True)

        bonus_reward = CLAIM_BONUS_REWARDS.get(post_doc["claim-streak"])

        # if bonus item reward, pick random item of given quality
        if bonus_reward != None:
            #pick random case
            random_container = random.choice(list(database.containers.keys()))
            item_pool = database.containers[random_container]["items"][bonus_reward]
            unformatted_name, float_val = gen_item(random.choice(item_pool))

            skin_data = database.skin_data[unformatted_name]

            e.add_field(name="You got a bonus item!", value=f"**{skin_data['formatted_name']}** - **{currency_str_format(skin_data['price'])}**", inline=False)
            e.color = rarity_color_dict[skin_data["rarity"]]
            e.set_image(url=skin_data["image_url"])         

            #create view
            view = discord.ui.View()
            inventory_button = discord.ui.Button(label="Add To Inventory", style=discord.ButtonStyle.green)
            sell_button = discord.ui.Button(label="Sell", style=discord.ButtonStyle.red)
            view.add_item(inventory_button)
            view.add_item(sell_button)

        await ctx.send(embed=e, view=view)

    else:
        time_left_seconds = TWELVE_HOURS - (int(time.time()) - post_doc["last-claim"])
        date_time = datetime.fromtimestamp( time_left_seconds )  
        time_left_formatted = date_time.strftime("%H:%M:%S")

        e = discord.Embed(
            title="You have already claimed your daily bonus!", 
            description=f"You can claim again in {time_left_formatted}", 
            color=discord.Color.red()
        )
        e.set_thumbnail(url=ctx.author.avatar.url)

        await ctx.send(embed=e)
