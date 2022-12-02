from discord.ext.commands import Context
from src.util import database
from src.util.format import currency_str_format
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
        e = discord.Embed(title="You have successfully claimed your daily reward!", color=discord.Color.green())
        e.set_thumbnail(url=ctx.author.avatar.url)

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
            container_data = database.containers[random_container]["items"][bonus_reward]
            skin = random.choice(container_data)

            skin_data = database.skin_data[skin]

             # select skin float
            min_float = skin_data["min_float"]
            max_float = skin_data["max_float"]

            float_value = random.random()
            
            #determine condition
            if float_value > 0 and float_value <= 0.1471:
                float_value = random.uniform(0.00, 0.07)
            elif float_value > 0.1471 and float_value <=  0.3939:
                float_value = random.uniform(0.07, 0.15)
            elif float_value > 0.3939 and float_value <= 0.8257:
                float_value = random.uniform(0.15, 0.38)
            elif float_value > 0.8257 and float_value <=   0.9007:
                float_value = random.uniform(0.38, 0.45)
            elif float_value > 0.9007 and float_value <= 1.0:
                float_value = random.uniform(0.45, 1)

            #linear interpolate between max and min float
            final_float = float_value * (max_float - min_float) + min_float

            for wear, upper in case_wear_ranges_lower.items():
                if final_float > upper:
                    condition = conditions[wear].lower() + " "
                    break

            #is it stattrak?
            if random.random() < 0.1:
                stattrak = "stattrak "
            else:
                stattrak = ""
            skin = stattrak + condition + skin
            skin_data = database.skin_data[skin]

            e.add_field(name="You got a bonus item!", value=f"**{skin_data['formatted_name']}** - **{currency_str_format(skin_data['price'])}**", inline=False)
            e.color = rarity_color_dict[skin_data["rarity"]]
            e.set_image(url=skin_data["image_url"])         

        await ctx.send(embed=e)

    else:
        time_left_seconds = TWELVE_HOURS - (int(time.time()) - post_doc["last-claim"])
        date_time = datetime.fromtimestamp( time_left_seconds )  
        time_left_formatted = date_time.strftime("%H:%M:%S")

        e = discord.Embed(
            title="You have already claimed your daily bonus!", 
            description=f"You have already claimed! You can claim again in {time_left_formatted}", 
            color=discord.Color.red()
        )
        e.set_thumbnail(url=ctx.author.avatar.url)

        await ctx.send(embed=e)
