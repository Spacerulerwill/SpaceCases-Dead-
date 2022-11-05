# this cog is for commands that affect the user's details and profile
# Commands:
# * register
# * claim
# * balance
# * inventory

import discord
from discord.ext import commands
from src.util import database
from src.util.constants import PREFIX, rarity_color_dict, INVENTORY_ELEMS_PER_PAGE
from datetime import timezone, datetime
from decimal import Decimal
from pymongo.collection import ReturnDocument

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
                "balance": 0,
                "last-claim": "01/01/1970",
                "inventory": [],
                "inventory-size": 5,
                "containers-opened": 0,
                "total-spent": 0,
                "total-return": 0,
            }
            database.user_actions[ctx.author.id] = None
            database.user_data.insert_one(profile)
            await ctx.send(f"Registered! Use `{PREFIX}claim` to claim some money!")
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
            #find and update current balance and last claim
            database.user_data.find_one_and_update({"_id": ctx.author.id}, {"$inc" :{"balance" : 10000}, "$set": {"last-claim" : str(dmy)}})

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
            return
        
        user_balance = (Decimal(user["balance"])/100).quantize(Decimal('0.01'))
        await ctx.send(f"{name} balance is: ${user_balance}")

    @balance.error
    async def balance_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Could not find that user!")

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

        if len(inventory_data) == 0:
            await ctx.send(f"User's inventory is empty! Use `{PREFIX}open` to start opening cases!")
            return

        total_inventory_value = 0

        #calculate inventory value
        for item in inventory_data:
            item_name = item["name"]
            total_inventory_value += database.skin_data[item_name]["price"]

        # check they have no current action
        current_action = database.user_actions[ctx.author.id]
        if current_action not in [None, database.OPENING_CASE]:
            await ctx.send(database.user_action_responses[current_action])
            return
        
        database.user_actions[ctx.author.id] = database.IN_INVENTORY

        page = 0
        item_index = 0
        inventory_pages = [inventory_data[x:x+INVENTORY_ELEMS_PER_PAGE] for x in range(0, len(inventory_data), INVENTORY_ELEMS_PER_PAGE)]
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
            nonlocal page, item_index, page_data
            if interact.user.id == ctx.author.id:
                if page == len(inventory_pages)-1:
                    page = 0
                else:
                    page += 1
                item_index = 0

                page_data = inventory_pages[page]
                await msg.edit(embed=await get_embed(), view=await get_view())

            await interact.response.defer()

        async def prev_button_callback(interact):
            nonlocal page, item_index, page_data
            if interact.user.id == ctx.author.id:
                if page == 0:
                    page = len(inventory_pages)-1
                else:
                    page -= 1
                item_index = 0

                page_data = inventory_pages[page]

                await msg.edit(embed=await get_embed(), view=await get_view())

            await interact.response.defer()

        async def sell_callback(interact):
            nonlocal item_index, page, total_inventory_value, inventory_pages, inventory_data, page_data
            if interact.user.id == ctx.author.id:
                item_unformatted_name = page_data[item_index]["name"]
                item_float = page_data[item_index]["float"]

                #remove from inventory
                new_user_data = database.user_data.find_one_and_update({
                    "_id": ctx.author.id}, 
                    {
                        "$pull": {"inventory": {"name": item_unformatted_name, "float": item_float}},
                        "$inc": {"balance": database.skin_data[item_unformatted_name]["price"]}
                    }, 
                    return_document=ReturnDocument.AFTER
                )

                total_inventory_value -= database.skin_data[item_unformatted_name]["price"]
                inventory_data = new_user_data["inventory"]
                inventory_pages = [inventory_data[x:x+INVENTORY_ELEMS_PER_PAGE] for x in range(0, len(inventory_data), INVENTORY_ELEMS_PER_PAGE)]
                
                if item_index > 1:
                    item_index -= 1
                elif len(inventory_pages) > 1:
                    page -= 1
                elif len(inventory_pages) == 0 and item_index == 0:
                    await msg.edit(content="Your inventory is now empty!", embed=None, view=None)
                    database.user_actions[ctx.author.id] = None
                    return

                page_data = inventory_pages[page]
                await msg.edit(embed=await get_embed(), view=await get_view())

            await interact.response.defer()

        async def close_callback(interact):
            if interact.user.id == ctx.author.id:
                database.user_actions[ctx.author.id] = None
                await msg.delete()
            else:
                await interact.response.defer()


        async def view_timeout_callback():
            database.user_actions[ctx.author.id] = None
            await msg.delete()
            
        async def get_embed():
            item_unformatted_name = page_data[item_index]["name"]
            item_float = page_data[item_index]["float"]
            item_data = database.skin_data[item_unformatted_name]
            item_formatted_name = item_data["formatted_name"]
            image_url = item_data["image_url"]
            rarity = item_data["rarity"]
            rarity_color = rarity_color_dict[rarity]
            item_price_int = item_data["price"]
            item_price = str((Decimal(item_price_int)/ 100).quantize(Decimal('0.01')))

            e = discord.Embed(title=f"{name}'s inventory - Page {page+1}/{len(inventory_pages)}", color=rarity_color)
            e.add_field(name="Item Name", value=item_formatted_name, inline=False)
            e.add_field(name="Price", value="$" + item_price)
            e.add_field(name="Rarity", value=rarity)
            e.add_field(name="Float", value=item_float)
            e.add_field(name="Inventory Index", value=str(item_index + (page*INVENTORY_ELEMS_PER_PAGE) + 1))
            e.set_footer(text=f"Total inventory value: ${str((Decimal(total_inventory_value) / 100).quantize(Decimal('0.01')))}\nWarning! Inventory will close after 30 seconds of inactivity")
            e.set_image(url=image_url)
            e.set_thumbnail(url=discord_user.avatar.url)

            return e

        async def get_view():
            nonlocal select

            view = discord.ui.View(timeout=30)
            select_options = []
            for index, item in enumerate(page_data):
                unformatted_name = item["name"]
                formatted_name = database.skin_data[unformatted_name]["formatted_name"]
                select_options.append(discord.SelectOption(label=formatted_name, value=index))

            select = discord.ui.Select(options=select_options, placeholder="Select a skin")
            select.callback = select_callback

            if len(inventory_pages) > 1:
                prev_button = discord.ui.Button(label="◀", style=discord.ButtonStyle.gray)
                prev_button.callback = prev_button_callback
                next_button = discord.ui.Button(label="▶", style=discord.ButtonStyle.gray)
                next_button.callback = next_button_callback

            sell_button = discord.ui.Button(label="Sell", style=discord.ButtonStyle.red)
            sell_button.callback = sell_callback
            close_button = discord.ui.Button(label="Close", style=discord.ButtonStyle.red)
            close_button.callback = close_callback

            view.add_item(select)
            if len(inventory_pages) > 1:
                view.add_item(prev_button)
                view.add_item(next_button)
            view.add_item(sell_button)
            view.add_item(close_button)
            view.on_timeout = view_timeout_callback
            

            return view
        

        msg = await ctx.send(embed=await get_embed(), view=await get_view())
        

# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(User(bot))