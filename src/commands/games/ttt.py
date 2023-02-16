import discord
import random
import numpy as np
from discord.ext.commands import Context
from discord.errors import NotFound
from src.util.decorators import requires
from src.util.embed_func import msg_embed_response, msg_embed

@requires(users_registered=True)
async def ttt(ctx:Context, player2:discord.Member):

    if ctx.author.id == player2.id:
        await msg_embed(ctx, "You can't play this game against yourself!")
        return

    e = discord.Embed(
        title="Tic Tac Toe", 
        description=f"""
        **{ctx.author.name}** vs **{player2.name}**
        Each player will have 10 seconds to make their move.
        **{player2.name}** must click the button below to accept!
        """,
        color=discord.Color.dark_theme()) 

    e.set_thumbnail(url=ctx.bot.user.display_avatar.url)
    e.set_footer(icon_url=ctx.author.display_avatar.url, text="Warning! Menu will close after 3 minutes!")

    view = discord.ui.View(timeout=180)

    async def view_timeout_callback():
        try:
            await msg.delete()
        except NotFound:
            pass

    view.on_timeout = view_timeout_callback

    opponent_accept = discord.ui.Button(style=discord.ButtonStyle.gray, label=player2.name, emoji="✅")
    opponent_ready = False
    async def opponent_callback(interact:discord.Interaction):
        nonlocal opponent_ready

        if interact.user.id != player2.id:
            await msg_embed_response(interact.response, "This is not your button!", ephemeral=True)
            return

        await start_game(ctx, player2, msg, interact)
    opponent_accept.callback = opponent_callback

    view.add_item(opponent_accept)

    msg = await ctx.send(embed=e, view=view)

async def start_game(ctx:Context, player2:discord.User, msg:discord.Message, interact:discord.Interaction):

    players = [ctx.author, player2]
    random.shuffle(players)
    counters = ["❌", "⭕"]
    turn_index = 0
    moves = 0
    game_over = False
    winner = None

    board = [[None for i in range(3)] for i in range(3)]

    async def button_callback(interact:discord.Interaction):
        nonlocal turn_index, winner, game_over, moves

        if game_over:
            await interact.response.defer()
            return

        if interact.user not in players:
            await msg_embed_response(interact.response, "You are not a part of this game!", ephemeral=True)
            return
        elif interact.user != players[turn_index]:
            await interact.response.defer()
            return

        button_index = int(interact.data["custom_id"])

        if board[button_index//3][button_index%3] is not None:
            await interact.response.defer()
            return

        board[button_index//3][button_index%3] = counters[turn_index]
        buttons[button_index].emoji = counters[turn_index]
        moves += 1
        
        winner = checkWin(board)
        if winner is not None:
            winner_user = players[counters.index(winner)]
            for button in buttons:
                button.disabled = True
            await interact.response.edit_message(content=f"{winner_user.name} won!", view=view)
            game_over = True
            return
        elif moves == 9:
            game_over = True
            for button in buttons:
                button.disabled = True
            await interact.response.edit_message(content=f"Draw!", view=view)
            return

        turn_index = (turn_index+1) % 2
        
        await interact.response.edit_message(content=f"{players[turn_index].name}'s turn", view=view)

    view = discord.ui.View(timeout=10)
    
    #whoever it times out on, the other player wins
    async def view_timeout_callback():

        nonlocal game_over, turn_index
        game_over = True

        turn_index = (turn_index+1) % 2
        winner = counters[turn_index]
        winner_user = players[counters.index(winner)]

        for button in buttons:
            button.disabled = True

        await msg.edit(content=f"{winner_user.name} won!", view=view)
        return

    view.on_timeout = view_timeout_callback
    buttons = [discord.ui.Button(label="\u200b", style=discord.ButtonStyle.gray, row=i%3, custom_id=str(i)) for i in range(9)]

    for i in range(9):
        buttons[i].callback = button_callback
        view.add_item(buttons[i])

    await interact.response.edit_message(content=f"{players[turn_index].name}'s turn", embed=None, view=view)

def checkRows(board):
    for row in board:
        if len(set(row)) == 1:
            return row[0]
    return None

def checkDiagonals(board):
    if len(set([board[i][i] for i in range(len(board))])) == 1:
        return board[0][0]
    if len(set([board[i][len(board)-i-1] for i in range(len(board))])) == 1:
        return board[0][len(board)-1]
    return None

def checkWin(board):
    #transposition to check rows, then columns
    for newBoard in [board, np.transpose(board)]:
        result = checkRows(newBoard)
        if result:
            return result
    return checkDiagonals(board)