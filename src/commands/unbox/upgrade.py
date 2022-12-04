import discord
from src.util import database
from src.util.constants import PREFIX
from src.util.string_util import round_sig_fig
from discord.ext.commands import Context

async def upgrade(ctx:Context, item_index:int, *args):
    result_item_name = " ".join(args[:]).strip().lower()

    user_data = database.user_data.find_one({"_id": ctx.author.id})

    #check user exists
    if user_data == None:
        await ctx.send(f"You are not registered! Use `{PREFIX}register` to register")
        return

    if item_index > len(user_data["inventory"]):
        await ctx.send(f"No item exists at index {item_index}")
        return

    item_index -= 1 
    start_item_name = user_data["inventory"][item_index]["name"]
    
    start_item_data = database.skin_data[start_item_name]

    try:
        result_item_data = database.skin_data[result_item_name]
    except KeyError:
        await ctx.send(f"No item exists with name `{result_item_name}`")

    if result_item_data["price"] <= start_item_data["price"]:
        await ctx.send("Result item must be worth more than starting item!")
        return

    price_multiplier = result_item_data["price"] / start_item_data["price"]
    percentage_chance = (1 / price_multiplier) * 100

    e = discord.Embed(description=f'**Upgrading**: {start_item_data["formatted_name"]}\n**To**: {result_item_data["formatted_name"]}')
    e.add_field(name="Price Multiplier", value=f"{round_sig_fig(price_multiplier, 2)}X")
    e.add_field(name="Chance", value=f"{round_sig_fig(percentage_chance, 2)}%")
    e.set_thumbnail(url=start_item_data["image_url"])
    e.set_image(url=result_item_data["image_url"])
    e.set_footer(icon_url=ctx.author.avatar.url, text="Warning! Upgrades will cancel after 30 seconds")
    await ctx.send(embed=e)
