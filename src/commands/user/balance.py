import discord
from discord.ext.commands import Context
from src.util import database
from src.util.lang import get_locale
from src.util.string_util import currency_str_format, round_sig_fig
from src.util.decorators import requires

@requires(users_registered=True)
async def balance(ctx: Context, member: discord.Member = None):
    if member is None:
        member = ctx.author

    user_data:dict = database.user_data.find_one({"_id": member.id})

    e = discord.Embed(title=get_locale(user_data["language"], "balance.embed.title", member.name), color=discord.Color.dark_theme())
    e.set_thumbnail(url=member.display_avatar.url)
    e.add_field(name=get_locale(user_data["language"], "balance.current"), value=currency_str_format(user_data["balance"]))

    if user_data["stats"]["total-spent"] == 0:
        total_return = 0
    else:
        total_return = round_sig_fig((user_data["stats"]["total-return"] * 100) / user_data["stats"]["total-spent"], 2)

    e.add_field(name=get_locale(user_data["language"], "balance.return"), value=str(total_return) + "%")

    await ctx.send(embed=e)
