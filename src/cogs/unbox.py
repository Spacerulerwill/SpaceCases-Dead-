
from discord.ext import commands
from discord import Embed
from src.util.constants import PREFIX, wear_dict, weapon_name_dict
from src.util.cases import CASES
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
        if not 3 <= len(query) <= 4:
            await ctx.send("Must provide 3 - 4 comma seperated arguments in format: weapon, skin name, condition, stattrak (optional)")
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

        stattrak = ""
        if len(query) == 4:
            if query[3] == "stattrak":
                stattrak = "StatTrak™ "
            else:
                await ctx.send("Argument 4 must be stattrak!")
                return

        reconstructed_name = f"{stattrak}{weapon} | {skin} {condition}"
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