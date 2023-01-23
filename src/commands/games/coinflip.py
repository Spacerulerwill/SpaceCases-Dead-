import discord
import random
from discord.ext.commands import Context
from src.util.images import CT_LOGO, T_LOGO
from src.util.embed_func import msg_embed
from src.util.string_util import currency_str_format
from src.util.decorators import requires
from src.util import database
from decimal import Decimal

@requires(users_registered=True)
async def coinflip(ctx:Context, t_ct:str, amount:Decimal):

    integer_amount = int(amount * Decimal('100'))

    if integer_amount <= 0:
        await msg_embed(ctx, "Amount to bet must be a positive number!")
        return

    if random.random() < 0.5:
        winner = "t"
        url = T_LOGO
    else:
        winner = "ct"
        url = CT_LOGO

    if t_ct == winner:

        # they won!
        update_result = database.user_data.update_one({"_id": ctx.author.id},
        [{
            "$set": {
                "balance": {
                    "$cond": {
                        "if": {"$gte": ["$balance", integer_amount]},
                        "then": {"$add": ["$balance", integer_amount]},
                        "else": "$balance"
                    }
                }
            }
        }])

        if update_result.modified_count == 0:
            await msg_embed(ctx, "You don't have enough balance to bet this much!")
            return

        e = discord.Embed(title=f"You Won {currency_str_format(integer_amount)}!", color=discord.Color.green()) 

    else:
        update_result = database.user_data.update_one({"_id": ctx.author.id},
        [{
            "$set": {
                "balance": {
                    "$cond": {
                        "if": {"$gte": ["$balance", integer_amount]},
                        "then": {"$subtract": ["$balance", integer_amount]},
                        "else": "$balance"
                    }
                }
            }
        }])

        if update_result.modified_count == 0:
            await msg_embed(ctx, "You don't have enough balance to bet this much!")
            return

        # they lost
        e = discord.Embed(title=f"You Lost {currency_str_format(integer_amount)}!", color=discord.Color.red())

        e.set_footer(text="Better luck next time!", icon_url=ctx.author.display_avatar.url)

    e.set_image(url=url)

    await ctx.send(embed=e)