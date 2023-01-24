import discord
from discord.errors import NotFound
import random
from discord.ext.commands import Context
from src.util.embed_func import msg_embed, msg_embed_response
from src.util.decorators import requires
from src.util import database

COSTS_MORE = True
COSTS_LESS = False

@requires(users_registered=True)
async def higher_lower(ctx:Context, difficulty:int):
    if not 3 <= difficulty <= 10:
        await msg_embed(ctx, "Amount must be in range 3 to 10")
        return

    # create start embed
    initial_item = random.choice(list(database.skin_data["skins"].keys()))
    initial_item_data = database.skin_data["skins"][initial_item]

    game_started = False

    e = discord.Embed(
        title=f"Higher or Lower", 
        description=f"""
        Welcome to the **Higher or Lower** game!
        
        In this game you must guess if the skin you see is more or less expensive than the previous one. Get all **{difficulty}** correct and you will win balance! 
        
        The first skin is shown to you below. Press the **Start** button to begin.
        """,
        color=discord.Color.dark_theme())
    
    e.set_image(url=initial_item_data["image_url"])
    e.set_footer(icon_url=ctx.author.display_avatar.url, text="Warning! Menu will close after 30 seconds")

    view = discord.ui.View(timeout=30)

    async def view_timeout_callback():
        try:
            if not game_started:
                await msg.delete()
        except NotFound:
            pass

    view.on_timeout = view_timeout_callback

    start_button = discord.ui.Button(label="Start",style=discord.ButtonStyle.green)

    # start game
    async def start_callback(interact:discord.Interaction):
        if interact.user.id != ctx.author.id:
            await msg_embed_response(interact.response, "This is not your game!")
            return
        
        nonlocal game_started
        game_started = True
        await interact.response.defer()
        await start_game(ctx, difficulty, initial_item_data, msg)

    start_button.callback = start_callback
    view.add_item(start_button)

    msg = await ctx.send(embed=e, view=view)

async def start_game(ctx:Context, difficulty:int, initial_skin_data:dict, msg:discord.Message):

    # get all skins prices
    random_skins = [random.choice(list(database.skin_data["skins"].keys())) for x in range(difficulty)]
    skin_data = [initial_skin_data] + [database.skin_data["skins"][skin] for skin in random_skins]
    correct_guesses = [skin_data[x]["price"] > skin_data[x-1]["price"] for x in range(1, difficulty + 1)]

    # view
    view = discord.ui.View(timeout=10)

    game_over = False

    # if button times out, the player has lost
    async def view_timeout_callback():
        if not game_over:
            e = discord.Embed(title="You Lost", description="You ran out of time!", color=discord.Color.red())
            await msg.edit(embed=e, view=None)

    view.on_timeout = view_timeout_callback

    less_button = discord.ui.Button(label="Less", style=discord.ButtonStyle.red)
    more_button = discord.ui.Button(label="More", style=discord.ButtonStyle.green)

    #call backs
    async def less_callback(interact:discord.Interaction):
        nonlocal guess_num, game_over

        if interact.user.id != ctx.author.id:
            await msg_embed_response(interact.response, "This is not your game!")
            return

        if guess_num + 1 < difficulty:

            if correct_guesses[guess_num] == COSTS_LESS:
                guess_num += 1
                await interact.response.edit_message(embed=get_embed(), view=view)
            else:
                game_over = True
                e = discord.Embed(title="You Lost!", description="You chose incorrectly!", color=discord.Color.red())
                await msg.edit(embed=e, view=None)
        else:
            # they made it to last one - they have won!
            game_over = True
            e = discord.Embed(title="You Won!", color=discord.Color.green())
            await msg.edit(embed=e, view=None)

    async def more_callback(interact:discord.Interaction):
        nonlocal guess_num, game_over
        if interact.user.id != ctx.author.id:
            await msg_embed_response(interact.response, "This is not your game!")
            return

        if guess_num + 1 < difficulty:
            if correct_guesses[guess_num] == COSTS_MORE:
                guess_num += 1
                await interact.response.edit_message(embed=get_embed(), view=view)
            else:
                game_over = True
                e = discord.Embed(title="You Lost!", description="You chose incorrectly!", color=discord.Color.red())
                await msg.edit(embed=e, view=None)
        else:
            game_over = True
            # they made it to last one - they have won!
            e = discord.Embed(title="You Won!", color=discord.Color.green())
            await msg.edit(embed=e, view=None)
    
    less_button.callback = less_callback
    more_button.callback = more_callback

    view.add_item(less_button)
    view.add_item(more_button)

    guess_num = 0

    def get_embed() -> discord.Embed:
        e = discord.Embed(title=f"Higher or Lower - {guess_num+1}/{difficulty}", description="Does this skin cost more or less than the previous?\nDecide within **10 seconds**")
        e.set_image(url=skin_data[guess_num+1]["image_url"])
        return e

    await msg.edit(embed=get_embed(), view=view)
