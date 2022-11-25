from discord.ext.commands import Context
from src.util import database
from src.util.constants import PREFIX, KEY_PRICE
import Levenshtein

async def open(ctx:Context, *args):
    container_name = " ".join(args[:]).strip().lower()

    user_data = database.user_data.find_one({"_id": ctx.author.id})

    #check user exists
    if user_data == None:
        await ctx.send(f"You are not registered! Use `{PREFIX}register` to register")
        return
    
    # check case exists
    try:
        container_data = database.containers[container_name]
    except KeyError:
        # try and find closest match
        highest_ratio = 0
        closest_match = None
        for key in database.containers.keys():
            ratio = Levenshtein.ratio(container_name, key)
            if ratio > highest_ratio:
                highest_ratio = ratio
                closest_match = key
        
        #if match is reasonably close enough
        if highest_ratio > 0.8:
            container_name = closest_match
            container_data = database.containers[container_name]
            await ctx.send(f'Container not found! Did you mean: `{container_data["formatted_name"]}`?')
        else:
            await ctx.send("Container not found!")
            return
    
    # check user has enough balance for case
    if user_data["balance"] < container_data["price"] + KEY_PRICE:
        await ctx.send("You don't have enough funds for this action!")
        return
    
