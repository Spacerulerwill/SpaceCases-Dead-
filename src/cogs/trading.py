"""
Copyright (C) 2022 William Redding - All Rights Reserved

Commands
~~~~~~~~
* trade
* trade new
* trade cancel
* trade send
* trade add 
* trade remove
* trade in
* trade out
* trade accept
* trade decline
* trades

See end of file for licence details
"""

import discord
from discord.ext import commands
from discord.ext.commands import Context
from src.util.constants import PREFIX

from src.commands.trading.trade import view_trade_in_creation
from src.commands.trading.trade_new import new
from src.commands.trading.trade_cancel import cancel
from src.commands.trading.trade_add import add
from src.commands.trading.trade_remove import remove
from src.commands.trading.trade_send import send
from src.commands.trading.trades import trades
from src.commands.trading.trade_in import view_incoming_trade
from src.commands.trading.trade_out import view_outgoing_trade
from src.commands.trading.trade_decline import decline
from src.commands.trading.trade_accept import accept

from typing import Literal, Optional


# initialise class
class Trading(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group()
    async def trade(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            await view_trade_in_creation(ctx)

    @trade.command()
    async def new(self, ctx: Context, member: discord.Member):
        await new(ctx, member)

    @trade.command()
    async def cancel(self, ctx: Context, recipient: discord.Member = None):
        await cancel(ctx, recipient)

    @trade.command()
    async def send(self, ctx: Context):
        await send(ctx)

    @trade.command()
    async def add(self, ctx: Context, in_out: Literal["in", "out"], item_index: int):
        await add(ctx, in_out, item_index)

    @trade.command()
    async def remove(self, ctx: Context, in_out: Literal["in", "out"], item_index: int):
        await remove(ctx, in_out, item_index)

    @commands.command()
    async def trades(
        self,
        ctx: Context,
        in_out: Optional[Literal["in", "out", "all"]],
        page: Optional[int] = 1,
    ):
        await trades(ctx, in_out, page)

    @trade.command()
    async def incoming(self, ctx: Context, sender: discord.Member):
        await view_incoming_trade(ctx, sender)

    @trade.command()
    async def out(self, ctx: Context, recipient: discord.Member):
        await view_outgoing_trade(ctx, recipient)

    @trade.command()
    async def accept(self, ctx: Context, sender: discord.Member):
        await accept(ctx, sender)

    @trade.command()
    async def decline(self, ctx: Context, sender: discord.Member):
        await decline(ctx, sender)


# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot: commands.Bot):
    await bot.add_cog(Trading(bot))


"""
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.

                            Preamble

  The GNU General Public License is a free, copyleft license for
software and other kinds of works.

  The licenses for most software and other practical works are designed
to take away your freedom to share and change the works.  By contrast,
the GNU General Public License is intended to guarantee your freedom to
share and change all versions of a program--to make sure it remains free
software for all its users.  We, the Free Software Foundation, use the
GNU General Public License for most of our software; it applies also to
any other work released this way by its authors.  You can apply it to
your programs, too.

  When we speak of free software, we are referring to freedom, not
price.  Our General Public Licenses are designed to make sure that you
have the freedom to distribute copies of free software (and charge for
them if you wish), that you receive source code or can get it if you
want it, that you can change the software or use pieces of it in new
free programs, and that you know you can do these things.

  To protect your rights, we need to prevent others from denying you
these rights or asking you to surrender the rights.  Therefore, you have
certain responsibilities if you distribute copies of the software, or if
you modify it: responsibilities to respect the freedom of others.

  For example, if you distribute copies of such a program, whether
gratis or for a fee, you must pass on to the recipients the same
freedoms that you received.  You must make sure that they, too, receive
or can get the source code.  And you must show them these terms so they
know their rights.

  Developers that use the GNU GPL protect your rights with two steps:
(1) assert copyright on the software, and (2) offer you this License
giving you legal permission to copy, distribute and/or modify it.

  For the developers' and authors' protection, the GPL clearly explains
that there is no warranty for this free software.  For both users' and
authors' sake, the GPL requires that modified versions be marked as
changed, so that their problems will not be attributed erroneously to
authors of previous versions.

  Some devices are designed to deny users access to install or run
modified versions of the software inside them, although the manufacturer
can do so.  This is fundamentally incompatible with the aim of
protecting users' freedom to change the software.  The systematic
pattern of such abuse occurs in the area of products for individuals to
use, which is precisely where it is most unacceptable.  Therefore, we
have designed this version of the GPL to prohibit the practice for those
products.  If such problems arise substantially in other domains, we
stand ready to extend this provision to those domains in future versions
of the GPL, as needed to protect the freedom of users.

  Finally, every program is threatened constantly by software patents.
States should not allow patents to restrict development and use of
software on general-purpose computers, but in those that do, we wish to
avoid the special danger that patents applied to a free program could
make it effectively proprietary.  To prevent this, the GPL assures that
patents cannot be used to render the program non-free.

  The precise terms and conditions for copying, distribution and
modification follow.
"""
