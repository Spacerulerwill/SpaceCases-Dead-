from discord.ext.commands import Context
from src.util import database
from src.util.string_util import currency_str_format
from src.util.skin_func import gen_item
from src.util.constants import ONE_DAY, rarity_color_dict
from src.util.embed_func import msg_embed
from src.util.decorators import requires
import discord
import time
import random

# 14 days
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

max_claim_streak = len(CLAIM_MONEY_AMOUNTS)

CLAIM_BONUS_REWARDS = {
    4: "classified",
    10: "covert",
    14: "rare items"
}

@requires(users_registered=True)
async def claim(ctx:Context):
    #update balance and set last claim to now if been twelve hours since last claim
    update_result = database.user_data.update_one({"_id": ctx.author.id},
    [   
        {
            "$set": {      
                 'claim-streak': {
                    "$let": {
                        "vars": {"daydiff": {"$subtract": [int(time.time())//ONE_DAY, {"$trunc": [{"$divide": ["$last-claim", ONE_DAY]}]}]}},
                        "in": {
                            "$switch": {
                                "branches": [
                                    {"case": {"$or": [
                                        {"$eq": ["$last-claim", 0]},
                                        {"$gt": ["$$daydiff", 1]}

                                    ]}, "then": 1},
                                    {"case": {"$eq": ["$$daydiff", 1]}, "then": {"$add": ["$claim-streak", 1]}}
                                ] ,
                                "default": "$claim-streak"
                            }
                        }
                    }
                },

                'balance': {
                    "$let": {
                        "vars": {
                            "daydiff": {"$subtract": [int(time.time())//ONE_DAY, {"$trunc": [{"$divide": ["$last-claim", ONE_DAY]}]}]},
                            "claim_money_amounts": CLAIM_MONEY_AMOUNTS
                        },
                        "in": {
                            "$cond": { # if first claim ever, or streak broken, add the first money amount
                                "if": {
                                    "$or": [
                                        {"$eq": ["$last-claim", 0]},
                                        {"$gt": ["$$daydiff", 1]}
                                    ]
                                },
                                "then": {"$add": ["$balance", {"$arrayElemAt": ["$$claim_money_amounts", 0]}]},
                                "else": { #otherwise if claim streak is greater than max, add the max
                                    "$cond": {
                                        "if": {
                                            "$eq": ["$$daydiff", 1]
                                        },
                                        "then": {
                                            "$cond": [
                                                {"$gte": ["$claim-streak", max_claim_streak]}, 
                                                {"$add": ["$balance", {"$arrayElemAt": ["$$claim_money_amounts", max_claim_streak-1]}]},
                                                {"$add": ["$balance", {"$arrayElemAt": ["$$claim_money_amounts", "$claim-streak"]}]}
                                            ]
                                        },
                                        "else": "$balance"
                                    }
                                }
                            }
                        }
                    }
                },

                'last-claim': {
                    "$let": {
                        "vars": {
                            "daydiff": {"$subtract": [int(time.time())//ONE_DAY, {"$trunc": [{"$divide": ["$last-claim", ONE_DAY]}]}]},
                            "claim_money_amounts": CLAIM_MONEY_AMOUNTS
                        },
                        "in": {
                            "$cond": {
                                "if": {
                                    "$or": [
                                        {"$gte": ["$$daydiff", 1]},
                                        {"$eq": ["$last-claim", 0]}
                                    ]
                                },
                                "then": int(time.time()),
                                "else": "$last-claim"
                            }
                        }
                    }
                }
            }
        }
    ])

    #if document modified
    if update_result.modified_count == 1:

        post_doc = database.user_data.find_one({"_id": ctx.author.id})

        #create embed
        e = discord.Embed(title="You have successfully claimed your daily reward!", description="You can claim again tomorrow", color=discord.Color.green())
        e.set_thumbnail(url=ctx.author.display_avatar.url)
        footer = "Note: Streaks reset 24 hours after your last claim"

        view = None
        
        prev_streak = post_doc["claim-streak"]
        if prev_streak != 0:
            prev_streak -= 1

        if post_doc["claim-streak"] >= 14: 
            e.add_field(name="Amount:", value="$300.00", inline=True)
        else:      
            e.add_field(name="Amount:", value=currency_str_format(CLAIM_MONEY_AMOUNTS[prev_streak]), inline=True)

        e.add_field(name="New Balance:", value=currency_str_format(post_doc["balance"]), inline=True)
        e.add_field(name="Streak 🔥", value=post_doc["claim-streak"], inline=True)

        bonus_reward = CLAIM_BONUS_REWARDS.get(post_doc["claim-streak"])

        interacted_with = False
        
        # callbacks
        async def sell_item():

            nonlocal interacted_with
            #change color to dark gray, remove footer, change balance to have balance of skin
            database.user_data.update_one({"_id": ctx.author.id}, {"$inc" :{"balance" : skin_price}})

            e.colour = discord.colour.Color.dark_gray()
            e.set_footer(text="")

            await msg.edit(embed=e, view=None)
            interacted_with = True
        
        async def sell_callback(interact:discord.Interaction):
            if ctx.author.id == interact.user.id:
                await sell_item()
            await interact.response.defer()
        
        async def inventory_callback(interact:discord.Interaction):
            nonlocal interacted_with
            if interact.user.id == ctx.author.id:
                
                # add to user inventory
                filter_ = {
                    '_id': ctx.author.id,
                    "$expr":{ "$lt" : ["$inventory-size", "$inventory-max-capacity"]}
                }
                update =  {
                    '$push': { 
                        'inventory':  {"name": unformatted_name, "float": float_val}
                    },
                    "$inc": {
                        "inventory-size": 1
                    }
                }

                update_result = database.user_data.update_one(filter_, update)    
                        
                if update_result.modified_count == 1:
                    e.colour = discord.colour.Color.green()
                    e.set_footer(text="")
                    await  msg.edit(embed=e, view=None)
                    
                elif update_result.modified_count == 0:
                    await msg_embed(ctx, "Your inventory is full! Sell an item or buy more inventory space")
            await interact.response.defer()

        #if not interacted with after 30 seconds, sell the item
        async def view_timeout_callback():
            if not interacted_with:
                await sell_item()
        
        # if bonus item reward, pick random item of given quality
        if bonus_reward != None:
           
            footer += "\nWarning: You have 3 minutes to claim your item!"
            #pick random case
            random_container = random.choice(list(database.containers.keys()))
            item_pool = database.containers[random_container]["items"][bonus_reward]
            unformatted_name, float_val = gen_item(random.choice(item_pool))

            skin_data = database.skin_data["skins"][unformatted_name]
            skin_price = skin_data["price"]

            e.add_field(name="You got a bonus item!", value=f"**{skin_data['formatted_name']}** - **{currency_str_format(skin_price)}**", inline=False)
            e.color = rarity_color_dict[skin_data["rarity"]]
            e.set_image(url=skin_data["image_url"])         

            #create view
            view = discord.ui.View()
            view.on_timeout = view_timeout_callback
            inventory_button = discord.ui.Button(label="Add To Inventory", style=discord.ButtonStyle.green)
            inventory_button.callback = inventory_callback
            sell_button = discord.ui.Button(label="Sell", style=discord.ButtonStyle.red)
            sell_button.callback = sell_callback
            view.add_item(inventory_button)
            view.add_item(sell_button)

        e.set_footer(text=footer)
        msg = await ctx.send(embed=e, view=view)

    else:
        await msg_embed(ctx, "You have already claimed your daily bonus! You can claim again tomorrow")