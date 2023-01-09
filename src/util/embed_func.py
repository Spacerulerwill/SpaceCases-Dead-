import discord
from discord.ext.commands import Context
from src.util.constants import PREFIX
from discord.ext import commands

# default message embed - send and return message
async def msg_embed(ctx:Context, msg_content:str, view:discord.ui.View=None):
    return await ctx.send(embed=discord.Embed(description=msg_content, color=discord.Color.dark_theme()), view=view)

def create_msg_embed(msg_content:str) -> discord.Embed:
    return discord.Embed(description=msg_content, color=discord.Color.dark_theme())

# edit existing message to be the default message embed
async def msg_embed_edit(msg:discord.Message, msg_content:str, view:discord.ui.View=None):
    await msg.edit(embed=discord.Embed(description=msg_content, color=discord.Color.dark_theme()), view=view)

# info message embed
def welcome_embed(bot: commands.Bot) -> discord.Embed:
    e = discord.Embed(
        description=f"""Hello! My name is **{bot.user.name}**

        I am CS:GO gambling and economy bot. With me you can:
        • Unbox your dream skins
        • Trade them with other users
        • Take a risk and upgrade them
        • And more coming soon!

        By default, users can open cases in any channel where they can type. This can cause a lot of clutter, so it is recommended you use `{PREFIX}config` to set up a room creation channel so users can unbox in their own threads

        Enjoy! - [Spacerulerwill](https://github.com/Spacerulerwill)

        Use `{PREFIX}info` to see this message again at anytime
        """,
        color=discord.Color.dark_theme()
    )

    e.set_thumbnail(url=bot.user.display_avatar.url)

    return e