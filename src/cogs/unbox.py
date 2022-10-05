from asyncio import QueueEmpty
from weakref import KeyedRef
from discord.ext import commands
from discord import Embed
from src.util.constants import CASES, PREFIX, wear_dict, weapon_name_dict
from src.util import database

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

    # view any weapon and see it's price
    @commands.command()
    async def inspect(self, ctx, *args):
        query = " ".join(args[:]).split(",")
        if len(query) != 3:
            await ctx.send("Must provide 3 comma seperated arguments in format: weapon, skin name, condition")
            return
        query = [_s.strip() for _s in query]

        try: 
            weapon = weapon_name_dict[query[0].lower()]
        except:
            await ctx.send("Weapon name not found!")
            return

        skin = query[1].title()

        try:
            condition = wear_dict[query[2].lower()]
        except KeyError:
            await ctx.send("Condition must be either: fn, mw, ft, ww, bs")
            return

        reconstructed_name = f"{weapon} | {skin} {condition}"
        #print(reconstructed_name)

        try:
            skin_price = database.skin_prices[reconstructed_name]
        except KeyError:
            await ctx.send("Invalid skin name!")
            return

        image_url = database.skin_static_data[reconstructed_name]["image_url"]
        color = int(database.skin_static_data[reconstructed_name]["rarity_color"], base=16)
        
        e = Embed(title=reconstructed_name, color=color)
        e.add_field(name="Current Market Price", value="$" + str(skin_price))
        e.set_image(url=image_url)
        await ctx.send(embed=e)
        
# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(UnboxCommands(bot))