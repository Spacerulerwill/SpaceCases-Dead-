from discord.ext.commands import Context
from src.util import database
from src.util.constants import LEADERBOARD_ELEMS_PER_PAGE

async def leaderboard(ctx:Context, page:int):
    page -= 1
    print(database.leaderboard[page*LEADERBOARD_ELEMS_PER_PAGE:(page+1)*LEADERBOARD_ELEMS_PER_PAGE])