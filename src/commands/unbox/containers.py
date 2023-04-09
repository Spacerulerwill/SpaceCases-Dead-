import discord
from discord.ext.commands import Context
from src.util.emojis import CASE_EMOJI, SOUVENIR_PACKAGE_EMOJI, STICKER_CAPSULE_EMOJI
from src.util.images import CASE, SOUVENIR_PACKAGE, STICKER_CAPSULE
from src.util.string_util import currency_str_format
from src.util.embed_func import msg_embed, msg_embed_response
from src.lang.lang import get_locale_fm
from src.util import database

cases = [
    (
        "Cases",
        [
            "revolution case",
            "recoil case",
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
            "operation hydra case",
        ],
    ),
    (
        "Cases",
        [
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
            "operation vanguard weapon case",
            "esports 2014 summer case",
            "operation breakout weapon case",
            "huntsman weapon case",
            "operation phoenix weapon case",
        ],
    ),
    (
        "Cases",
        [
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

souvenir_packages = [
    (
        "Souvenir Packages",
        [
            "rio 2022 vertigo souvenir package",
            "rio 2022 nuke souvenir package",
            "rio 2022 ancient souvenir package",
            "rio 2022 overpass souvenir package",
            "rio 2022 dust ii souvenir package",
            "rio 2022 mirage souvenir package",
            "rio 2022 inferno souvenir package",
            "antwerp 2022 vertigo souvenir package",
            "antwerp 2022 nuke souvenir package",
            "antwerp 2022 ancient souvenir package",
            "antwerp 2022 overpass souvenir package",
            "antwerp 2022 dust ii souvenir package",
            "antwerp 2022 mirage souvenir package",
            "antwerp 2022 inferno souvenir package",
        ],
    ),
    (
        "Souvenir Packages",
        [
            "stockholm 2021 vertigo souvenir package",
            "stockholm 2021 nuke souvenir package",
            "stockholm 2021 ancient souvenir package",
            "stockholm 2021 overpass souvenir package",
            "stockholm 2021 dust ii souvenir package",
            "stockholm 2021 mirage souvenir package",
            "stockholm 2021 inferno souvenir package",
            "berlin 2019 vertigo souvenir package",
            "berlin 2019 nuke souvenir package",
            "berlin 2019 train souvenir package",
            "berlin 2019 overpass souvenir package",
            "berlin 2019 dust ii souvenir package",
            "berlin 2019 mirage souvenir package",
            "berlin 2019 inferno souvenir package",
        ],
    ),
    (
        "Souvenir Packages",
        [
            "katowice 2019 nuke souvenir package",
            "katowice 2019 train souvenir package",
            "katowice 2019 cache souvenir package",
            "katowice 2019 overpass souvenir package",
            "katowice 2019 dust ii souvenir package",
            "katowice 2019 mirage souvenir package",
            "katowice 2019 inferno souvenir package",
            "london 2018 nuke souvenir package",
            "london 2018 train souvenir package",
            "london 2018 cache souvenir package",
            "london 2018 overpass souvenir package",
            "london 2018 dust ii souvenir package",
            "london 2018 mirage souvenir package",
            "london 2018 inferno souvenir package",
        ],
    ),
    (
        "Souvenir Packages",
        [
            "boston 2018 nuke souvenir package",
            "boston 2018 train souvenir package",
            "boston 2018 cache souvenir package",
            "boston 2018 overpass souvenir package",
            "boston 2018 cobblestone souvenir package",
            "boston 2018 mirage souvenir package",
            "boston 2018 inferno souvenir package",
            "krakow 2017 nuke souvenir package",
            "krakow 2017 train souvenir package",
            "krakow 2017 cache souvenir package",
            "krakow 2017 overpass souvenir package",
            "krakow 2017 cobblestone souvenir package",
            "krakow 2017 mirage souvenir package",
            "krakow 2017 inferno souvenir package",
        ],
    ),
    (
        "Souvenir Packages",
        [
            "atlanta 2017 nuke souvenir package",
            "atlanta 2017 train souvenir package",
            "atlanta 2017 cache souvenir package",
            "atlanta 2017 overpass souvenir package",
            "atlanta 2017 cobblestone souvenir package",
            "atlanta 2017 mirage souvenir package",
            "atlanta 2017 dust ii souvenir package",
            "cologne 2016 nuke souvenir package",
            "cologne 2016 train souvenir package",
            "cologne 2016 cache souvenir package",
            "cologne 2016 overpass souvenir package",
            "cologne 2016 cobblestone souvenir package",
            "cologne 2016 mirage souvenir package",
            "cologne 2016 dust ii souvenir package",
        ],
    ),
    (
        "Souvenir Packages",
        [
            "mlg columbus 2016 nuke souvenir package",
            "mlg columbus 2016 train souvenir package",
            "mlg columbus 2016 cache souvenir package",
            "mlg columbus 2016 overpass souvenir package",
            "mlg columbus 2016 cobblestone souvenir package",
            "mlg columbus 2016 inferno souvenir package",
            "mlg columbus 2016 mirage souvenir package",
            "mlg columbus 2016 dust ii souvenir package",
            "dreamhack cluj-napoca 2015 train souvenir package",
            "dreamhack cluj-napoca 2015 cache souvenir package",
            "dreamhack cluj-napoca 2015 overpass souvenir package",
            "dreamhack cluj-napoca 2015 cobblestone souvenir package",
            "dreamhack cluj-napoca 2015 inferno souvenir package",
            "dreamhack cluj-napoca 2015 mirage souvenir package",
            "dreamhack cluj-napoca 2015 dust ii souvenir package",
        ],
    ),
    (
        "Souvenir Packages",
        [
            "esl one cologne 2015 train souvenir package",
            "esl one cologne 2015 cache souvenir package",
            "esl one cologne 2015 overpass souvenir package",
            "esl one cologne 2015 cobblestone souvenir package",
            "esl one cologne 2015 inferno souvenir package",
            "esl one cologne 2015 mirage souvenir package",
            "esl one cologne 2015 dust ii souvenir package",
            "esl one katowice 2015 overpass souvenir package",
            "esl one katowice 2015 cobblestone souvenir package",
            "esl one katowice 2015 cache souvenir package",
            "esl one katowice 2015 nuke souvenir package",
            "esl one katowice 2015 mirage souvenir package",
            "esl one katowice 2015 inferno souvenir package",
            "esl one katowice 2015 dust ii souvenir package",
        ],
    ),
    (
        "Souvenir Packages",
        [
            "dreamhack 2014 overpass souvenir package",
            "dreamhack 2014 cobblestone souvenir package",
            "dreamhack 2014 cache souvenir package",
            "dreamhack 2014 nuke souvenir package",
            "dreamhack 2014 mirage souvenir package",
            "dreamhack 2014 inferno souvenir package",
            "dreamhack 2014 dust ii souvenir package",
            "esl one cologne 2014 overpass souvenir package",
            "esl one cologne 2014 cobblestone souvenir package",
            "esl one cologne 2014 cache souvenir package",
            "esl one cologne 2014 nuke souvenir package",
            "esl one cologne 2014 mirage souvenir package",
            "esl one cologne 2014 inferno souvenir package",
            "esl one cologne 2014 dust ii souvenir package",
        ],
    ),
]

all_containers = cases + souvenir_packages

select_values = [all_containers, cases, souvenir_packages]
select_images = [CASE, CASE, SOUVENIR_PACKAGE, STICKER_CAPSULE]

prev_button = discord.ui.Button(label="◀", style=discord.ButtonStyle.gray)
next_button = discord.ui.Button(label="▶", style=discord.ButtonStyle.gray)

async def containers(ctx: Context, page: int = 1):
    user_data = database.user_data.find_one({"_id": ctx.author.id})

    if user_data is None:
        lang = "en"
    else:
        lang = user_data["lang"]

    if page <= 0 or page > len(all_containers):
        await msg_embed(ctx, get_locale_fm(lang, "invalid_page"))
        return

    page -= 1

    container_page_data = all_containers

    def get_embed(select_value:int=None):
        if select_value is None:
            try:
                select_value = int(select.values[0])
            except IndexError:
                select_value = 0
            
        container_type, containers = container_page_data[page]

        e = discord.Embed(
            title=get_locale_fm(
                lang, "containers.embed.title", page + 1, len(container_page_data), select_labels[select_value]
            ),
            description=get_locale_fm(lang, "containers.embed.description"),
            color=discord.Color.dark_theme(),
        )

        page_field = ""
        for container in containers:
            container_data = database.containers[container]

            page_field += f'• {container_data["formatted_name"]} - **{currency_str_format(container_data["price"])}**\n'
        e.add_field(name=container_type, value=page_field)
        e.set_footer(text=get_locale_fm(lang, "containers.embed.footer"))
        e.set_thumbnail(url=select_images[select_value])
        return e

    # callbacks
    async def prev_callback(interact: discord.Interaction):
        if interact.user.id != ctx.author.id:
            await msg_embed_response(
                interact.response,
                get_locale_fm(lang, "not_your_button"),
                ephemeral=True,
            )
            return

        nonlocal page

        if page > 0:
            page -= 1
        else:
            page = len(container_page_data) - 1
        await interact.response.edit_message(embed=get_embed())

    async def next_callback(interact: discord.Interaction):
        if interact.user.id != ctx.author.id:
            await msg_embed_response(
                interact.response,
                get_locale_fm(lang, "not_your_button"),
                ephemeral=True,
            )
            return

        nonlocal page

        if page < len(container_page_data) - 1:
            page += 1
        else:
            page = 0
        await interact.response.edit_message(embed=get_embed())

    async def select_callback(interact: discord.Interaction):
        if interact.user.id != ctx.author.id:
            await msg_embed_response(
                interact.response,
                get_locale_fm(lang, "not_your_select"),
                ephemeral=True,
            )
            return

        nonlocal container_page_data, page
        select_value = int(select.values[0])
        container_page_data = select_values[select_value]
        page = 0
        await interact.response.edit_message(embed=get_embed(select_value))

    async def view_timeout_callback():
        await msg.delete()

    # create view
    view = discord.ui.View(timeout=30)
    view.on_timeout = view_timeout_callback

    # create select menu
    select = discord.ui.Select(
        options=[
            discord.SelectOption(label=get_locale_fm(lang, "containers.select.label.all_containers"), value=0),
            discord.SelectOption(label=get_locale_fm(lang, "containers.select.label.cases"), value=1, emoji=CASE_EMOJI),
            discord.SelectOption( 
                label=get_locale_fm(lang, "containers.select.label.souvenir_packages"), value=2, emoji=SOUVENIR_PACKAGE_EMOJI
            ),
            discord.SelectOption(label=get_locale_fm(lang, "containers.select.label.sticker_capsules"), value=3, emoji=STICKER_CAPSULE_EMOJI),
        ]
    ) 
    select_labels = [select_option.label for select_option in select.options]
    select.callback = select_callback
    view.add_item(select)

    # create next and previous buttons
    prev_button.callback = prev_callback
    view.add_item(prev_button)

    next_button.callback = next_callback
    view.add_item(next_button)

    msg = await ctx.send(embed=get_embed(), view=view)
