import discord
from discord.ext.commands import Context
from src.util.decorators import requires
from src.util import database
from src.util.string_util import round_sig_fig

@requires(users_registered=True)
async def stats(ctx:Context, member:discord.Member):
    if member is None:
        member = ctx.author

    user_data = database.user_data.find_one({"_id": member.id})

    if user_data["total-spent"] == 0:
        total_return = 0
    else:
        total_return = round_sig_fig((user_data["total-return"] * 100) / user_data["total-spent"], 2)
    
    e = discord.Embed(title=f"{member.name}'s Statistics", 
        description=f"""**Containers Opened** - {user_data['containers-opened']}
        **Return** - {total_return}%
        """,
        color=discord.Color.dark_theme()
    )
    e.set_thumbnail(url=member.display_avatar.url)

    await ctx.send(embed=e)
