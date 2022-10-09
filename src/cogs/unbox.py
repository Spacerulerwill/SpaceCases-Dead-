
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
            await ctx.send("Must provide 3 - 4 comma seperated arguments in format: weapon, skin name, condition, modifier: stattrak | souvenir (optional)")
            return

        query = [_s.strip() for _s in query]

        try:
            weapon = weapon_name_dict[query[0].lower()]
        except KeyError:
            await ctx.send("Weapon not found!")
            return

        skin = query[1].title()

        weapon_skin = f"{weapon} | {skin}"

        if weapon_skin not in database.csgostash_static_data:
            await ctx.send(f"{skin} is not an available skin for {weapon}")

        try:
            wear = wear_dict[query[2].lower()]
        except KeyError:
            await ctx.send("Wear must be either fn, mw, ft, ww, bs")

        if (len(query) == 4):
            modifier = query[3].lower()

            if modifier not in ["stattrak", "souvenir"]:
                modifier = ""
                await ctx.send("Modifier argument must be either stattrak or souvenir!")
                return
            elif modifier == "stattrak":
                if database.csgostash_static_data[weapon_skin]["stattrak"] == True:
                    modifier = "StatTrak™ "
                else:
                    await ctx.send(f"{weapon_skin} is not available as {modifier}")
                    return

            elif modifier == "souvenir":
                if database.csgostash_static_data[weapon_skin]["souvenir"] == True:
                    modifier = "Souvenir "
                else:
                    await ctx.send(f"{weapon_skin} is not available as {modifier}")
                    return
        else:
            modifier = ""

        full_item = f"{modifier}{weapon} | {skin} {wear}"

        if database.csgostash_static_data[f"{weapon} | {skin}"]["is_special"]:
            full_item = "★ " + full_item

        try:
            skin_price = database.skin_prices[full_item]
            if skin_price == None:
                skin_price = "Unknown"
            else:
                skin_price = "$" + str(skin_price)
        except KeyError:
            await ctx.send(f"{modifier}{weapon} | {skin} is not available as {wear}")
            return

        image_url = database.skin_static_data[full_item]["image_url"]
        color = int(database.skin_static_data[full_item]["rarity_color"], base=16)
        rarity = database.skin_static_data[full_item]["rarity"]
        
        e = Embed(title=full_item, color=color)
        e.add_field(name="Current Market Price", value=skin_price)
        e.add_field(name="Rarity", value=rarity, inline=True)
        e.set_image(url=image_url)
        await ctx.send(embed=e)

        
        
# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(UnboxCommands(bot))