import discord
from src.util import database
from src.util.lang import get_locale
from discord.ext.commands import Context
from src.commands.trading.trade_func import create_item_str
from src.util.decorators import requires
from src.util.embed_func import msg_embed

@requires(users_registered=True)
async def decline(ctx:Context, sender:discord.Member):
    lang = database.user_data.find_one({"_id": ctx.author.id})["language"]
    deleted_document = database.trade_requests.find_one_and_delete({"_id": sender.id, "recipient-id": ctx.author.id, "send-timestamp": {"$ne": 0}})
    
    if deleted_document is None:
        await msg_embed(ctx, get_locale(lang, "no_incoming_trade", sender.name))
    else:
        #inform recipient trade has been declined
        e = discord.Embed(title=get_locale(lang, "trade_decline.author_embed.description", sender.name), color=discord.Color.red())
        
        await msg_embed(ctx, embed=e)

        #inform original sender that their request was declined
        e = discord.Embed(title=get_locale(lang, "trade_decline.sender_embed.title", ctx.author.name), color=discord.Color.red())
        e.set_thumbnail(url=sender.display_avatar.url)

        you_wanted = create_item_str(lang, deleted_document["recipient-items"])
        for_your = create_item_str(lang, deleted_document["sender-items"])
        e.add_field(name=get_locale(lang, "you_wanted"), value=you_wanted)
        e.add_field(name=get_locale(lang, "for_your"), value=for_your)
        await sender.send(embed=e)

