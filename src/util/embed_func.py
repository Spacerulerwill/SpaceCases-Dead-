"""
Copyright (C) 2023 William Redding - All Rights Reserved

General use embed related functionality

Functions
~~~~~~~~~
* msg_embed
* msg_embed_response
* create_msg_embed
* msg_embed_edit
* welcome_embed

See end of file for licence details
"""

import discord
from discord.ext.commands import Context
from src.lang.lang import get_locale_fm
from discord.ext import commands


async def msg_embed(
    ctx: Context, msg_content: str, view: discord.ui.View = None
) -> discord.Message:
    """send an embed with dark theme with a text description via a context

    Args:
        ctx: the context to send with
        msg_content: the text for the embed
        view: default: None - an optional view to send with the message
    Returns:
        The discord message that was sent
    """
    return await ctx.send(
        embed=discord.Embed(description=msg_content, color=discord.Color.dark_theme()),
        view=view,
    )


async def msg_embed_response(
    response: discord.InteractionResponse, msg_content: str, ephemeral: bool = False
):
    """send an embed with dark theme with a text description via a interact response

    Args:
        response: the interaction response to send with
        msg_content: the text for the embed
        ephemeral: default: False - whether the msg is ephemeral (only recipient can see)
    Returns:
        The discord message that was sent
    """
    return await response.send_message(
        embed=discord.Embed(description=msg_content, color=discord.Color.dark_theme()),
        ephemeral=ephemeral,
    )


def create_msg_embed(msg_content: str) -> discord.Embed:
    """create an embed with dark theme with a text description

    Args:
        msg_content: the text for the embed
    Returns:
        The embed created
    """
    return discord.Embed(description=msg_content, color=discord.Color.dark_theme())


async def msg_embed_edit(
    msg: discord.Message, msg_content: str, view: discord.ui.View = None
):
    """edit a message and replace its embed and view with a dark theme text embed and a view

    Args:
        msg: the msg to edit
        msg_content: the text for the embed
        view: optional: a view to send with the message
    """
    await msg.edit(
        embed=discord.Embed(description=msg_content, color=discord.Color.dark_theme()),
        view=view,
    )


def welcome_embed(lang: str, bot: commands.Bot) -> discord.Embed:
    """
    send the bots welcome message

    Args:
        bot - the bot

    Args:
        msg: the msg to edit
        msg_content: the text for the embed
        view: optional: a view to send with the message
    """
    e = discord.Embed(
        description=get_locale_fm(lang, "welcome_message", bot.user.name),
        color=discord.Color.dark_theme(),
    )

    e.set_thumbnail(url=bot.user.display_avatar.url)

    return e


"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
