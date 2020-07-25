import discord
import asyncio
from discord.ext import commands
from Settings.MongoManager import MongoManager
from Settings.MyUtility import checkin_member, checkin_guild, get_prefix, db_gld, db_mbr
from RPGPackage.RPGModule import start_rpg

WHITE = 0xfffffe

def rpg_init(user: discord.User):
    mbr_data: dict = checkin_member(user)
    db_mbr.SetObject({"member_id": mbr_data["member_id"]}, start_rpg)

def rpg_close(user: discord.User):
    mbr_data: dict = checkin_member(user)
    default_data: dict = start_rpg
    for el in default_data:
        subdata = None
        dlist: list = el.split(".")
        for n in dlist:
            if subdata is None:
                subdata = mbr_data[n]
            else:
                subdata = subdata[n]
        default_data[el] = subdata
    db_mbr.UnsetItem({"member_id": mbr_data["member_id"]}, default_data)

class Adventure(commands.Cog):

    # Cog Constructor
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Commands Area
    # Start RPG command, initialize user character and send it to database
    @commands.command(name="start")
    async def _start_rpg(self, ctx: commands.Context):
        mbr_data = checkin_member(ctx.author)
        if mbr_data is not None:
            if "MAX-STAT" in mbr_data:
                await ctx.send(f"__**{ctx.author.name}, You have already start your character, type {get_prefix(ctx.guild)}stat to see your current progress.**__")
            else:
                async with ctx.typing():
                    hm: discord.Message = await ctx.send("*Building your character, this might take a seconds.*")
                    rpg_init(ctx.author)
                    emb = discord.Embed(title=f"👱‍♂️ Character has been Created", colour=WHITE, 
                                        description=f"Welcome {ctx.author.name}! Check your stat in {get_prefix(ctx.guild)}stat")
                    await hm.delete()
                await ctx.send(embed=emb)

    # Close RPG account, delete user current progress
    @commands.command(name="close")
    async def _close_rpg(self, ctx: commands.Context):
        mbr_data: dict = checkin_member(ctx.author)
        if mbr_data is not None:
            if "MAX-STAT" in mbr_data:
                emb = discord.Embed(title="Close Progress?",
                    description="Are you sure you want to close your current progress?\n"
                        "> Warning! This may delete all of your RPG attribute like items, equipments, stats, and moves you have learned.",
                    colour=discord.Colour(WHITE))
                emb.set_footer(text="React ✅ to continue or ❌ to abort")
                hm: discord.Message = await ctx.send(embed=emb)
                await hm.add_reaction("✅")
                await hm.add_reaction("❌")
                try:
                    r, u = await self.bot.wait_for(event= "reaction_add", timeout= 30.0, check= lambda reaction, user: True if (str(reaction.emoji) == "❌" or str(reaction.emoji) == "✅") and user == ctx.author else False)
                    await hm.delete()
                    if str(r.emoji) == "✅":
                        hm = await ctx.send("*Deleting your progress, Wait for a moment.*")
                        rpg_close(ctx.author)
                        emb = discord.Embed(title= f"⚰️ RIP | {ctx.author.name}", colour=WHITE)
                        emb.set_image(url="https://trello-attachments.s3.amazonaws.com/5ee1ce52bb089c7be29e6b4f/5efc6fe38c338f1f7b4799a8/ef81e5b6732bcdc5cd6eebe093486a31/Coffin_Dance_GIF.gif")
                        await ctx.send(embed=emb)
                    else:
                        await ctx.send("*Aborted*")
                except asyncio.TimeoutError:
                    await hm.delete()
                    await ctx.send("*Request Timeout*")
            else:
                await ctx.send(f"__**{ctx.author.name}, You haven't start your character, type {get_prefix(ctx.guild)}start to begin.**__")

    # Adventure command, random benefit for user
    @commands.command(name="adventure", aliases=["adv"])
    async def _adv(self, ctx: commands.Context):
        pass

def setup(bot: commands.Bot):
    bot.add_cog(Adventure(bot))