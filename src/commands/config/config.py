import discord
from discord.ext.commands import Context, Bot, TextChannelConverter
from src.util import database
from src.util.lang import get_locale
from pymongo import ReturnDocument
from src.util.constants import PREFIX
from src.util.embed_func import msg_embed, create_msg_embed, msg_embed_response
import asyncio

config_options = [
    {
        "name": "config.options.room_channel.name",
        "value": "unbox_room_creation_channel_id",
        "default_value": None,
        "type": discord.TextChannel,
        "description": "config.options.room_channel.description",
        "options": [],
        "response_text": "config.options.room_channel.response_embed_text",
        "post_func": lambda result: result.id,
    },
]


async def config_menu(bot: Bot, ctx: Context):
    user_data = database.user_data.find_one({"_id": ctx.author.id})

    if user_data is None:
        lang = "en"
    else:
        lang = user_data["lang"]

    option_index = 0

    async def get_config_embed() -> discord.Embed:
        post_doc = database.guild_data.find_one_and_update(
            {"_id": ctx.guild.id},
            {
                "$setOnInsert": {
                    "unbox_room_creation_channel_id": None,
                }
            },
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

        option = config_options[option_index]
        current_value = post_doc[option["value"]]

        match option["type"]:
            case discord.TextChannel:
                if current_value is not None:
                    try:
                        current_value = bot.get_channel(
                            post_doc[option["value"]]
                        ).mention
                    except AttributeError:
                        # channel no longer exists
                        current_value = get_locale(lang, "backtick_none")
                        database.guild_data.update_one(
                            {"_id": ctx.guild.id}, {"$set": {option["value"]: None}}
                        )
                else:
                    current_value = get_locale(lang, "backtick_none")
            case _:
                current_value = f"`{current_value}`"

        description = f"""{get_locale(lang, option["description"])}
        
        {get_locale(lang, "config.current_value", current_value)}"""

        e = discord.Embed(
            title=f'**{get_locale(lang, option["name"])}**',
            description=description,
            color=discord.Color.dark_theme(),
        )
        e.set_thumbnail(url=bot.user.display_avatar.url)
        e.set_footer(
            text=get_locale(lang, "config.menu.footer")
        )

        return e

    # VIEW
    async def view_timeout_callback():
        await msg.delete()

    view = discord.ui.View()
    view.on_timeout = view_timeout_callback

    select_options = [discord.SelectOption(label=get_locale(lang, config_options[0]["name"]), value=0)]

    if len(config_options) > 1:
        select_options += [
            discord.SelectOption(label=get_locale(lang, option["name"]), value=count + 1)
            for count, option in enumerate(config_options[1:])
        ]

    select = discord.ui.Select(options=select_options)

    # SELECT MENU
    async def select_callback(interact: discord.Interaction):
        if interact.user.id != ctx.author.id:
            await msg_embed_response(
                interact.response, get_locale(lang, "not_your_select"), ephemeral=True
            )
            return

        nonlocal option_index
        option_index = int(select.values[0])

        await interact.response.edit_message(embed=await get_config_embed())

    select.callback = select_callback

    edit_button = discord.ui.Button(
        label=get_locale(lang, "button.edit"), style=discord.ButtonStyle.gray
    )

    async def edit_callback(interact: discord.Interaction):
        if interact.user.id != ctx.author.id:
            await msg_embed_response(
                interact.response, get_locale(lang, "not_your_button"), ephemeral=True
            )
            return

        selected_option = config_options[option_index]

        name = get_locale(lang, selected_option["name"])

        # send response embed
        await msg_embed_response(interact.response, get_locale(lang, selected_option["response_text"]))

        # if no options, must be a user input
        if len(selected_option["options"]) == 0:

            def check(message: discord.Message):
                return message.author == ctx.author and message.channel == ctx.channel

            try:
                response: discord.Message = await bot.wait_for(
                    "message", check=check, timeout=30
                )

                if response:
                    # choose right conversion for each type
                    match selected_option["type"]:
                        case discord.TextChannel:
                            converter = lambda msg: TextChannelConverter().convert(
                                ctx, msg
                            )
                        case _:
                            converter = selected_option["type"]

                    # try conversion
                    try:
                        result = await converter(response.content)

                        # apply post func if neccesary
                        if selected_option["post_func"] is not None:
                            result = selected_option["post_func"](result)

                        database.guild_data.update_one(
                            {"_id": ctx.guild.id},
                            {"$set": {selected_option["value"]: result}},
                        )

                        await interact.message.edit(embed=await get_config_embed())

                        await response.reply(
                            embed=create_msg_embed(
                                get_locale(lang, "config.successful_change", name, response.content)
                            )
                        )
                    except:
                        await response.reply(
                            embed=create_msg_embed(get_locale(lang, "config.conversion_fail"))
                        )
            except asyncio.TimeoutError:
                await msg_embed(
                    interact.followup,
                    get_locale(lang, "config.no_response", name)
                )
        else:
            # if has options provide an option menu embed
            pass

    edit_button.callback = edit_callback

    clear_button = discord.ui.Button(
        style=discord.ButtonStyle.red, label=get_locale(lang, "button.clear")
    )

    async def clear_callback(interact: discord.Interaction):
        if interact.user.id != ctx.author.id:
            await msg_embed_response(
                interact.response, get_locale(lang, "not_your_button"), ephemeral=True
            )
            return

        selected_option = config_options[option_index]
        database.guild_data.update_one(
            {"_id": ctx.guild.id},
            {"$set": {selected_option["value"]: selected_option["default_value"]}},
        )

        await interact.message.edit(embed=await get_config_embed())

        await msg_embed_response(
            interact.response,
            get_locale(lang,"config.set_default_value", get_locale(lang, selected_option["name"], get_locale(lang, str(selected_option["default_value"]))))
        )

    clear_button.callback = clear_callback

    view.add_item(select)
    view.add_item(edit_button)
    view.add_item(clear_button)

    msg = await ctx.send(embed=await get_config_embed(), view=view)
