import discord
from discord.ext.commands import Context

# default message embed
async def msg_embed(ctx:Context, msg_content:str, view:discord.ui.View=None):
    return await ctx.send(embed=discord.Embed(description=msg_content, color=discord.Color.dark_theme()), view=view)

# edit existing message to be the default message embed
async def msg_embed_edit(msg:discord.Message, msg_content:str, view:discord.ui.View=None):
    await msg.edit(embed=discord.Embed(description=msg_content, color=discord.Color.dark_theme()), view=view)