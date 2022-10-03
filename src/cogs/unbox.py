from discord.ext import commands
from src.util.constants import CASES, PREFIX
from src.util.database import skin_static_data, skin_prices
from discord.ext import tasks

# initialise class
class UnboxCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # unbox a case
    @commands.command()
    async def unbox(self, ctx, *args):
        # combine args to make word
        case_name = " ".join(args[:]).strip().lower()
        if "case" not in args:
            case_name += " case"

        if case_name in CASES:
            pass
        else:
            await ctx.send(f"Invalid case! Use {PREFIX}cases to see the list of available cases.")

    @commands.command()
    async def price(self, ctx, *args):
        skin_name = " ".join(args[:]).strip()
        print(skin_prices[skin_name])
        
# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(UnboxCommands(bot))