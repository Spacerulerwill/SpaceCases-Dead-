import discord
from discord.ext.commands import Context, Bot, TextChannelConverter, ChannelNotFound
from src.util import database
from pymongo import ReturnDocument
from src.util.constants import PREFIX
from src.util.embed_func import create_msg_embed

config_options = [
    {
        "name": "Unboxing Room Creation Channel",
        "value": "unbox-room-creation-channel-id",
        "type": discord.TextChannel,
        "description": "Channel used to create rooms to unbox cases in",
        "options": [],
        "response-embed": create_msg_embed("Respond to this message with name of text channel"),
        "post-func": lambda result: result.id
    }
]

async def config_menu(bot:Bot, ctx:Context):

    option_index = 0

    async def get_config_embed() -> discord.Embed:

        post_doc = database.guild_data.find_one_and_update(
            {"_id": ctx.guild.id},
            {
                "$setOnInsert": {
                    "unbox-room-creation-channel-id": None,
                }
            },
            upsert=True,
            return_document=ReturnDocument.AFTER
        )

        option = config_options[option_index]
        current_value = post_doc[option["value"]]

        match option["type"]:
            case discord.TextChannel:
                if current_value is not None:
                    current_value = bot.get_channel(post_doc[option["value"]])
                    
        description = f'{option["description"]}\nCurrent Value: `{current_value}`'

        e = discord.Embed(
            title=f'**{option["name"]}**', 
            description=description, 
            color=discord.Color.dark_theme()
        )
        e.set_thumbnail(url=bot.user.display_avatar.url)
        e.set_footer(text="Warning! Menu will close itself after 3 minutes of inactivity")

        return e

    async def view_timeout_callback():
        await msg.delete()

    view = discord.ui.View()
    view.on_timeout = view_timeout_callback
    
    select_options = [discord.SelectOption(label=config_options[0]["name"], value=config_options[0]["value"], default=True)]

    if len(config_options) > 1:
        select_options += [discord.SelectOption(label=option["name"], value=option["value"]) for option in config_options[1:]]

    select = discord.ui.Select(options=select_options)

    edit_button = discord.ui.Button(label="Edit", style=discord.ButtonStyle.gray)

    async def edit_callback(interact:discord.Interaction):
        selected_option = config_options[option_index]
        
        #send response embed
        await interact.response.send_message(embed=selected_option["response-embed"])

        # if no options, must be a user input
        if len(selected_option["options"]) == 0:

            def check(message: discord.Message):
                return message.author == ctx.author and message.channel == ctx.channel

            response:discord.Message = await bot.wait_for('message', check=check, timeout=30)

            # choose right conversion for each type
            match selected_option["type"]:
                case discord.TextChannel:
                    converter = lambda msg: TextChannelConverter().convert(ctx, msg)
                case _:
                    converter = selected_option["type"]

            # try conversion
            try:
                result = await converter(response.content)

                # apply post func if neccesary
                if selected_option["post-func"] is not None:
                    result = selected_option["post-func"](result)

                database.guild_data.update_one({"_id": ctx.guild.id}, {"$set": {selected_option["value"]: result}})

                await msg.edit(embed=await get_config_embed())
            except:
                await response.reply(embed=create_msg_embed("Conversion Failiure"))
        else:
            # if has options provide an option menu embed
            pass

    edit_button.callback = edit_callback

    view.add_item(select)
    view.add_item(edit_button)

    msg = await ctx.send(embed=await get_config_embed(), view=view)