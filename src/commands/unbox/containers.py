import discord
from discord.ext.commands import Context
from src.util.constants import PREFIX

containerlist_pages = {
    "Cases": 
        ["""Operation Riptide Case
        Snakebite Case
        Broken Fang Case
        Fracture Case
        Prisma 2 Case
        Shattered Web Case
        CS20 Case
        Prisma Case
        Danger Zone Case
        Horizon Case
        Clutch Case
        Spectrum 2 Case""",

        """Operation Hydra Case
        Spectrum Case
        Glove Case
        Gamma 2 Case
        Gamma Case
        Chroma 3 Case
        Operation Wildfire Case
        Revolver Case
        Shadow Case
        Falcion Case
        Chroma 2 Case
        Chroma Case""",
        """
        Operation Vanguard Weapon Case
        eSports 2014 Summer Case
        Operation Breakout Weapon Case
        Huntsman Weapon Case
        Operation Phoenix Weapon Case
        CSGO Weapon Case 3
        Winter Offensive Weapon Case
        eSports 2013 Winter Case
        CSGO Weapon Case 2
        Operation Bravo Case
        eSports 2013 Case
        CSGO Weapon Case
        """]
}

len_containerlist_pages = len(containerlist_pages)

async def containers(ctx:Context, page:int = 1):
    if page <= 0 or page > len_containerlist_pages:
        await ctx.send("Invalid page number!")
        return

    page -= 1
    page_title, page_fields = list(containerlist_pages.items())[page]
    
    e = discord.Embed(
        title=f"Page {page+1}/{len_containerlist_pages}", 
        description=f"Use `{PREFIX}container <container>` to see a container's contents and `{PREFIX}open <container>` to open one"
    )

    for field in page_fields:
        e.add_field(name=page_title, value=field)

    await ctx.send(embed=e)