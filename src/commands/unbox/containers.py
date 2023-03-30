import discord
from discord.ext.commands import Context
from src.util.constants import PREFIX, KEY_PRICE
from src.util.string_util import currency_str_format
from src.util.embed_func import msg_embed, msg_embed_response
from src.util.lang import get_locale
from src.util import database

containerlist_pages = [
    (
        "Cases",
        [
            "revolution case",
            "operation riptide case",
            "snakebite case",
            "operation broken fang case",
            "fracture case",
            "prisma 2 case",
            "shattered web case",
            "cs20 case",
            "prisma case",
            "danger zone case",
            "horizon case",
            "clutch case",
            "spectrum 2 case",
        ],
    ),
    (
        "Cases",
        [
            "operation hydra case",
            "spectrum case",
            "glove case",
            "gamma 2 case",
            "gamma case",
            "chroma 3 case",
            "operation wildfire case",
            "revolver case",
            "shadow case",
            "falchion case",
            "chroma 2 case",
            "chroma case",
        ],
    ),
    (
        "Cases",
        [
            "operation vanguard weapon case",
            "esports 2014 summer case",
            "operation breakout weapon case",
            "huntsman weapon case",
            "operation phoenix weapon case",
            "csgo weapon case 3",
            "winter offensive weapon case",
            "esports 2013 winter case",
            "csgo weapon case 2",
            "operation bravo case",
            "esports 2013 case",
            "csgo weapon case",
        ],
    ),
]

len_containerlist_pages = len(containerlist_pages)


async def containers(ctx: Context, page: int = 1):
    user_data = database.user_data.find_one({"_id": ctx.author.id})

    if user_data is None:
        lang = "en"
    else:
        lang = user_data["lang"]

    if page <= 0 or page > len_containerlist_pages:
        await msg_embed(ctx, get_locale(lang, "invalid_page"))
        return

    page -= 1

    def get_embed():
        container_type, containers = containerlist_pages[page]

        e = discord.Embed(
            title=get_locale(
                lang, "containers.embed.title", page + 1, len_containerlist_pages
            ),
            description=get_locale(
                lang, "containers.embed.description", PREFIX, PREFIX
            ),
            color=discord.Color.dark_theme(),
        )

        page_field = ""
        for container in containers:
            container_data = database.containers[container]

            page_field += f'{container_data["formatted_name"]} - **{currency_str_format(container_data["price"])}**\n'
        e.add_field(name=container_type, value=page_field)
        e.set_footer(
            text=get_locale(
                lang, "containers.embed.footer", currency_str_format(KEY_PRICE)
            )
        )
        return e

    # callbacks
    async def prev_callback(interact: discord.Interaction):
        if interact.user.id != ctx.author.id:
            await msg_embed_response(
                interact.response, get_locale(lang, "not_your_button"), ephemeral=True
            )
            return

        nonlocal page

        if page > 0:
            page -= 1
        else:
            page = len_containerlist_pages - 1
        await interact.response.edit_message(embed=get_embed(), view=view)

    async def next_callback(interact: discord.Interaction):
        if interact.user.id != ctx.author.id:
            await msg_embed_response(
                interact.response, get_locale(lang, "not_your_button"), ephemeral=True
            )
            return

        nonlocal page

        if page < len_containerlist_pages - 1:
            page += 1
        else:
            page = 0
        await interact.response.edit_message(embed=get_embed(), view=view)

    async def view_timeout_callback():
        await msg.delete()

    # create next and prev page buttons
    view = discord.ui.View(timeout=30)
    view.on_timeout = view_timeout_callback

    prev_button = discord.ui.Button(label="◀", style=discord.ButtonStyle.gray)
    prev_button.callback = prev_callback
    view.add_item(prev_button)

    next_button = discord.ui.Button(label="▶", style=discord.ButtonStyle.gray)
    next_button.callback = next_callback
    view.add_item(next_button)

    msg = await ctx.send(embed=get_embed(), view=view)
