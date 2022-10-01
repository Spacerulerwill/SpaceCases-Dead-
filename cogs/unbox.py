from discord.ext import commands

#initialise class
class UnboxCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #unbox a case
    @commands.command()
    async def unbox(self, ctx):
        pass
        
# this setup function needs to be in every cog in order for the bot to be able to load it
async def setup(bot):
    await bot.add_cog(UnboxCommands(bot))