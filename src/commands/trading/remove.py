import discord
from src.util import database
from src.util.constants import PREFIX
from discord.ext.commands import Context
from src.commands.trading.trade import send_trade_embed_view

async def remove(ctx:Context, item_index:int):
    pass