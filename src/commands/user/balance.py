import discord
from discord.ext.commands import Context
from src.util import database
from src.lang.lang import get_locale_fm
from src.util.string_util import currency_str_format, round_sig_fig
from src.util.decorators import requires


@requires(users_registered=True)
async def balance(ctx: Context, member: discord.Member):
    if member is None:
        member = ctx.author

    user_data: dict = database.user_data.find_one({"_id": member.id})
    lang = user_data["lang"]

    e = discord.Embed(
        title=get_locale_fm(lang, "balance.embed.title", member.name),
        color=discord.Color.dark_theme(),
    )
    e.set_thumbnail(url=member.display_avatar.url)
    e.add_field(
        name=get_locale_fm(lang, "balance.current"),
        value=currency_str_format(user_data["balance"]),
    )

    if user_data["stats"]["total_spent"] == 0:
        total_return = 0
    else:
        total_return = round_sig_fig(
            (user_data["stats"]["total_return"] * 100)
            / user_data["stats"]["total_spent"],
            2,
        )

    e.add_field(
        name=get_locale_fm(lang, "balance.return"), value=str(total_return) + "%"
    )

    await ctx.send(embed=e)