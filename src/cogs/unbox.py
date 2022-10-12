
from faulthandler import dump_traceback_later
from discord.ext import commands
from discord import Embed
from src.util.constants import PREFIX, wear_dict, weapon_name_dict
from src.util.cases import CASES
from src.util import database
from src.util.format import remove_skin_name_formatting

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
            await ctx.send("Must provide 3 - 4 comma seperated arguments in format: weapon, skin name, condition, modifier: stattrak | souvenir (optional)")
            return

        #argument formatting to convert arguments to useable skin name
        query = [_s.strip() for _s in query]

        weapon = query[0]

        skin = query[1]

        unformatted_weapon = remove_skin_name_formatting(weapon)
        unformatted_skin = remove_skin_name_formatting(skin)
        unformatted_name = f"{unformatted_weapon} | {unformatted_skin}"            

        wear = query[2].lower()

        # vanilla knives making everything needlessly complicated
        if unformatted_skin == "vanilla":
            wear = "no_wear"

        modifier = ""
        if len(query) == 4:
            modifier = query[3].lower()

        if unformatted_name not in database.csgostash_static_data:
            await ctx.send("Skin does not exist!")
            return
        else:
            if modifier not in database.csgostash_static_data[unformatted_name]:
                await ctx.send(f"Skin modifier can only be stattrak or souvenir")
                return
            else:
                if modifier == "stattrak":
                        modifier = "StatTrak™ "
                elif modifier == "souvenir":
                    modifier = "Souvenir"
                else:
                    await ctx.send(f"Skin not available as {modifier}")
                    return
        try:
            if database.csgostash_static_data[unformatted_name]["is_special"]:
                formatted_name = "★ " + modifier + database.csgostash_static_data[unformatted_name]["formatted_name"]
            else:
                formatted_name = modifier + database.csgostash_static_data[unformatted_name]["formatted_name"]
        except KeyError:
            await ctx.send(f"Skin does not exist!")
            return

        if wear not in wear_dict:
            await ctx.send(f"Wear must be one of the following: fn, mw, ft, ww, bs")
            return
        else:
            wear = wear_dict[wear]
            
        formatted_name = formatted_name + " " + wear

        full_name = remove_skin_name_formatting(formatted_name)

        # get price and details and create embed
        try:
            skin_price = database.skin_prices[full_name]
            if skin_price == None:
                skin_price = "Unknown"
            else:
                skin_price = "$" + str(skin_price)
        except:
            await ctx.send(f"Skin not available in that condition")
            return

        image_url = database.skin_static_data[full_name]["image_url"]
        color = int(database.skin_static_data[full_name]["rarity_color"], base=16)
        rarity = database.skin_static_data[full_name]["rarity"]
        
        e = Embed(title=formatted_name, color=color)
        e.add_field(name="Market Price", value=skin_price)
        e.add_field(name="Rarity", value=rarity, inline=True)

        if len(query) == 4 and query[3] == "souvenir":
            tournament = database.skin_static_data[full_name]["tournament"]
            e.add_field(name="Tournament", value=tournament)
            
        e.set_image(url=image_url)
        await ctx.send(embed=e)
        
# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(UnboxCommands(bot))