import discord
from discord.ext.commands import Context
from src.util import database
from src.util.decorators import requires 
from src.util.string_util import currency_str_format
from src.util.embed_func import msg_embed
from decimal import Decimal

@requires(users_registered=True)
async def transfer(ctx:Context, member: discord.Member, amount:float):
    if member is ctx.author:
        await msg_embed(ctx, "You cannot transfer money to yourself!")
        return

    if amount <= 0:
        await msg_embed(ctx, "Amount to transfer must be greater than 0")
        return

    #convert amount to cents
    amount = int(Decimal(amount) * 100)

    #start a session to multi docuemnt atomic transaction
    with database.mongo_client.start_session() as session:
        with session.start_transaction():
            update_result = database.user_data.update_one({"_id": ctx.author.id}, 
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
            }
            }], session=session)

            if update_result.modified_count == 1:
                other_update_result = database.user_data.update_one({"_id":member.id}, {"$inc": {"balance": amount}}, session=session)
                if other_update_result.matched_count == 0:
                    await ctx.send(f"{member.name} is not registered!")
                    session.abort_transaction()
                    return
                
                await msg_embed(ctx, f"Successfully transferred {currency_str_format(amount)} to {member.name}'s account")
            else:
                await ctx.send("You have insufficient funds!")