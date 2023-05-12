import discord
from src.util import database
from src.lang.lang import get_locale_fm
from src.util.constants import rarity_color_dict
from src.util.decorators import requires
from src.util.string_util import currency_str_format, get_inspect_link_3D
from src.util.item_func import get_item_embed
from src.util.embed_func import msg_embed
from discord.ext.commands import Context


@requires(users_registered=True)
async def inspect(ctx: Context, member: discord.Member, item_index: int):
    if member is None:
        member = ctx.author

    user_data = database.user_data.find_one({"_id": member.id})
    lang = user_data["lang"]
    user_inventory = list(user_data["inventory"])

    if item_index > len(user_inventory):
        await msg_embed(
            ctx, get_locale_fm(lang, "inventory.not_found_index", item_index)
        )
        return

    item_index -= 1

    item = user_inventory[item_index]

    unformatted_name = item["name"]
    item_data = database.skin_data["skins"][unformatted_name]
    e = get_item_embed(lang, item_data)

    if item_data["item_type"] == "weapon":
        e.add_field(name=get_locale_fm(lang, "float"), value=str(item["float"]))

    e.set_footer(
        icon_url=member.display_avatar.url, text=f"This item belongs to {member.name}"
    )

    await ctx.send(embed=e)