# this cog is for commands that affect the user's details and profile
# Commands:
# * register
# * claim
# * balance
# * inventory

import discord
from discord.ext import commands
from src.util import database
from src.util.constants import PREFIX, rarity_color_dict
from datetime import timezone, datetime
from decimal import Decimal

# initialise class
class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #register a profile
    @commands.command(description="Register for a bank account", usage=f"""
    `{PREFIX}register`
    """)
    async def register(self, ctx):
        if database.user_data.find_one({"_id": ctx.author.id}) == None:
            profile = {
                "_id": ctx.author.id,
                "balance": '0.0',
                "last-claim": "01/01/1970",
                "inventory": [],
                "inventory-size": 5,
                "containers-opened": 0,
                "total-spent": '0.0',
                "total-return": '0.0',
            }

            database.user_data.insert_one(profile)
            await ctx.send(f"Registered! Use `{PREFIX}profile` to see your profile")
        else:
            await ctx.send("You are already registered!")

    @commands.command(description="Claim daily money allowance", usage=f"""
    `{PREFIX}claim`
    """)
    async def claim(self, ctx):

        #check if user is registed
        user = database.user_data.find_one({"_id": ctx.author.id})

        if user == None:
            await ctx.send(f"You aren't registed! Use `{PREFIX}register` to register")
            return

        #if user is registed
        #get last claim time
        last_claim = user['last-claim']
        
        #convert to date time
        dt = datetime.strptime(last_claim ,"%d/%m/%Y")
        dt = dt.strftime("%d/%m/%Y")
        
        #get current time
        now = datetime.now(tz=timezone.utc)
        dmy = now.strftime("%d/%m/%Y")

        #see if it has been atleast a day
        if dmy != dt:
            #add money
            current_balance = Decimal(user['balance'])
            
            database.user_data.update_one({"_id":ctx.author.id},{"$set" :{"balance" : str(current_balance+100)}})

            #update last claim date
            database.user_data.update_one({"_id":ctx.author.id},{"$set" :{"last-claim" : str(dmy)}})

            await ctx.send("You claimed $100! Come back tomorrow to claim again")
        else:
            await ctx.send("You must wait until tomorrow to claim again!")

    @commands.command(description="Check a user's balance", usage=f"""
    `{PREFIX}balance <user>`
    **Arguments**
    `<user>` - optional - user to check balance of
    """)
    async def balance(self, ctx, member: discord.Member = None):
        #if used an @ to specify a member
        if member == None:
            member = ctx.author
            name = "Your"
        else:
            name = f"{member.display_name}'s"
            
        #get user
        user = database.user_data.find_one({"_id": member.id})

        if user == None:
            if member == ctx.author:
                await ctx.send(f"You are not registered! Use `{PREFIX}register` to register")
            else:
                await ctx.send(f'{member.display_name} has not registered yet')
        else:
            user_balance = Decimal(user["balance"])
            await ctx.send(f"{name} balance is: ${'{:.2f}'.format(user_balance)}")

    @commands.command(description="View a user's inventory", usage=f"""
    `{PREFIX}inventory <user>`
    **Arguments**
    `<user>` - optional - user whos inventory to check
    """)
    async def inventory(self, ctx, discord_user: discord.Member = None):

        if discord_user == None:
            discord_user = ctx.author
            

        user = database.user_data.find_one({"_id": discord_user.id})

        if user == None:
            await ctx.send(f"User is not registed! Use `{PREFIX}register` to register")
            return

        inventory_data = user["inventory"]

        total_inventory_value = Decimal('0.0')

        #calculate inventory value
        for item in inventory_data:
            item_name = item["name"]
            price = Decimal(database.skin_data[item_name]["price"])
            total_inventory_value += price

        if len(inventory_data) == 0:
            await ctx.send(f"User's inventory is empty! Use `{PREFIX}open` to start opening cases!")
            return

        page = 0
        item_index = 0
        inventory_pages = [inventory_data[x:x+25] for x in range(0, len(inventory_data), 25)]
        page_data = inventory_pages[page]

        select = None

        name = discord_user.name

        async def select_callback(interact):
            nonlocal item_index
            if interact.user.id == ctx.author.id:
                item_index = int(select.values[0])

                await msg.edit(embed=await get_embed())
            
            await interact.response.defer()

        async def next_button_callback(interact):
            nonlocal page, item_index
            if interact.user.id == ctx.author.id:
                if page == len(inventory_pages)-1:
                    page = 0
                else:
                    page += 1
                item_index = 0

                await msg.edit(embed=await get_embed(), view=await get_view())

            await interact.response.defer()

        async def prev_button_callback(interact):
            nonlocal page, item_index
            if interact.user.id == ctx.author.id:
                if page == 0:
                    page = len(inventory_pages)-1
                else:
                    page -= 1
                item_index = 0

                await msg.edit(embed=await get_embed(), view=await get_view())

            await interact.response.defer()

        async def get_embed():
            item_unformatted_name = page_data[item_index]["name"]
            item_float = page_data[item_index]["float"]
            item_data = database.skin_data[item_unformatted_name]
            item_formatted_name = item_data["formatted_name"]
            image_url = item_data["image_url"]
            rarity = item_data["rarity"]
            rarity_color = rarity_color_dict[rarity]
            item_price = item_data["price"]

            e = discord.Embed(title=f"{name}'s inventory - Page {page+1}/{len(inventory_pages)}\n{item_formatted_name}", color=rarity_color)
            e.add_field(name="Price", value="$" + item_price)
            e.add_field(name="Rarity", value=rarity)
            e.add_field(name="Float", value=item_float)
            e.add_field(name="Inventory Index", value=str(item_index + (page*25) + 1))
            e.set_footer(text=f"Total inventory value: ${total_inventory_value}")
            e.set_image(url=image_url)
            e.set_thumbnail(url=discord_user.avatar.url)

            return e

        async def get_view():
            nonlocal select

            view = discord.ui.View()

            select_options = []
            for index, item in enumerate(page_data):
                unformatted_name = item["name"]
                formatted_name = database.skin_data[unformatted_name]["formatted_name"]
                select_options.append(discord.SelectOption(label=formatted_name, value=index))

            select = discord.ui.Select(options=select_options, placeholder="Select a skin")
            select.callback = select_callback

            prev_button = discord.ui.Button(label="◀", style=discord.ButtonStyle.gray)
            prev_button.callback = prev_button_callback
            next_button = discord.ui.Button(label="▶", style=discord.ButtonStyle.gray)
            next_button.callback = next_button_callback
            view.add_item(select)
            view.add_item(prev_button)
            view.add_item(next_button)

            return view
        
        msg = await ctx.send(embed=await get_embed(), view=await get_view())

# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(User(bot))