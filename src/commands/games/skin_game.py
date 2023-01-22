import discord
import random
import asyncio
import Levenshtein
from discord.ext.commands import Context
from src.util import database
from src.util.decorators import requires
from src.util.embed_func import msg_embed
from src.util.string_util import remove_skin_name_formatting, currency_str_format

# GAME PRICES
SKIN_GAME_PRICE = 250
SKIN_GAME_REWARD = 750

NOT_ENOUGH_FUNDS_MSG = f"You do not have enough funds for this action. You need **{currency_str_format(SKIN_GAME_PRICE)}** to play!"
WIN_MSG = f"You guessed **correctly!** You win **{currency_str_format(SKIN_GAME_REWARD)}**"

@requires(users_registered=True)
async def skin_game(ctx:Context):

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
        await msg_embed(ctx, NOT_ENOUGH_FUNDS_MSG)
        return

    e = discord.Embed(
        title="Guess the Skin!",
        description="Reply with the name of the skin within 10 seconds!\nDo **not** include the wear or the weapon name!",
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
            await msg_embed(ctx, WIN_MSG)
            database.user_data.update_one({"_id": ctx.author.id}, {"$inc": {"balance": SKIN_GAME_REWARD}})
        else:
            await msg_embed(ctx, f"You guessed **incorrectly!** The correct answer was `{skin_name}`")

    except asyncio.TimeoutError:
        await msg_embed(ctx, f"You did not reply in time! The correct answer was `{skin_name}`")
    
