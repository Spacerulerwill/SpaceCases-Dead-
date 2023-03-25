import discord
import random
import asyncio
import Levenshtein
from discord.ext.commands import Context
from src.util import database
from src.util.lang import get_locale
from src.util.decorators import requires
from src.util.embed_func import msg_embed
from src.util.string_util import remove_skin_name_formatting, currency_str_format

# GAME PRICES
SKIN_GAME_PRICE = 250
SKIN_GAME_REWARD = 750

SKIN_GAME_REWARD_STR = currency_str_format(SKIN_GAME_REWARD)

@requires(users_registered=True)
async def skin_game(ctx:Context):
    lang = database.user_data.find_one({"_id": ctx.author.id})["language"]
    # check user has enough to play
    update_result = database.user_data.update_one({"_id": ctx.author.id},
    [{
        "$set": {
            "balance": {
                "$cond": {
                    "if": {"$gte": ["$balance", SKIN_GAME_PRICE]},
                    "then": {"$subtract": ["$balance", SKIN_GAME_PRICE]},
                    "else": "$balance"
                }
            }
        }
    }])

    if update_result.modified_count == 0:
        await msg_embed(ctx, get_locale(lang, "not_enough_funds"))
        return

    e = discord.Embed(
        title=get_locale(lang, "skin_game.embed.title"),
        description=get_locale(lang, "skin_game.embed.description"),
        color=discord.Color.dark_theme()
    )

    random_item = random.choice(list(database.skin_data["skins"].keys()))
    random_item_data = database.skin_data["skins"][random_item]
    skin_name = remove_skin_name_formatting(random_item_data["formatted_name"].split(" | ")[1]).strip()
    
    image_url = random_item_data["image_url"]

    e.set_image(url=image_url)

    await ctx.send(embed=e)

    def check(message: discord.Message):
        return message.author == ctx.author and message.channel == ctx.channel

    try:
        response:discord.Message = await ctx.bot.wait_for('message', check=check, timeout=10)
        
        guess = response.content.strip().lower()

        if Levenshtein.ratio(guess, skin_name) > 0.8:
            await msg_embed(ctx, get_locale(lang, "skin_game.won", SKIN_GAME_REWARD_STR))
            database.user_data.update_one({"_id": ctx.author.id}, {"$inc": {"balance": SKIN_GAME_REWARD}})
        else:
            await msg_embed(ctx, get_locale(lang, "skin_game.lost.incorrect_guess", skin_name))

    except asyncio.TimeoutError:
        await msg_embed(ctx, get_locale(lang, "skin_game.lost.out_of_time", skin_name))
    
