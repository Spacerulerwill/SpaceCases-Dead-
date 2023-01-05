import discord
from discord.ext.commands import Context, Bot
from discord.ext import commands

async def config_menu(bot:commands.Bot, ctx:Context):
    e = discord.Embed(
        title=f"Config Menu - {ctx.guild.name}",
        color=discord.Color.dark_theme(),
    )
    e.set_thumbnail(url=bot.user.display_avatar.url)

    await ctx.send(embed=e)