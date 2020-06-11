import discord
import asyncio
from discord.ext import commands
from Settings.MongoManager import MongoManager
from Settings.MyUtility import checkin_member, checkin_guild, rpg_close, rpg_init, get_prefix

WHITE = 0xfffffe

class Adventure(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.gdb = MongoManager(collection= "guilds")
        self.mdb = MongoManager(collection= "members")

    # Event Listener Area

    @commands.Cog.listener()
    async def on_ready(self):
        print("Adventure World has been Generated.")

    # Commands Area

    @commands.command(name= "start", pass_context= True)
    async def _start_rpg(self, ctx: commands.Context):
        mbr_data: dict = checkin_member(ctx.author.id)
        if "MAX-STAT" in mbr_data:
            await ctx.send(f"__**You have already start your character, type {get_prefix(ctx.guild.id)}stat to see your current progress.**__")
        else:
            hm: discord.Message = await ctx.send("*Building your character, this might take a seconds.*")
            rpg_init(ctx.author.id)
            emb = discord.Embed(
                title= f"👱‍♂️ Character has been Created",
                description= f"Welcome {ctx.author.name}! Check your stat in {get_prefix(ctx.author.id)}stat",
                colour= discord.Colour(WHITE)
                )
            await hm.delete()
            await ctx.send(embed= emb)

    @commands.command(name= "close", pass_context= True)
    async def _close_rpg(self, ctx: commands.Context):
        mbr_data: dict = checkin_member(ctx.author.id)
        if "MAX-STAT" in mbr_data:
            emb = discord.Embed(
                title= "Close Progress?",
                description= "Are you sure you want to close your current progress?\n"
                    "> Warning! This may delete all of your RPG attribute like items, equipments, stats, and moves you have learned.",
                colour= discord.Colour(WHITE)
                )
            emb.set_footer(text= "React ✅ to continue or ❌ to abort")
            hm: discord.Message = await ctx.send(embed= emb)
            await hm.add_reaction("✅")
            await hm.add_reaction("❌")
            try:
                r: discord.Reaction
                u: discord.User
                r, u = await self.bot.wait_for(
                    event= "reaction_add",
                    check= lambda reaction, user: True if (str(reaction.emoji) == "❌" or str(reaction.emoji) == "✅") and user == ctx.author else False,
                    timeout= 30.0
                    )
                if str(r.emoji) == "✅":
                    await hm.delete()
                    hm = await ctx.send("*Deleting your progress, Wait for a moment.*")
                    rpg_close(ctx.author.id)
                    await ctx.send(embed= discord.Embed(title= f"⚰️ RIP | {ctx.author.name}", colour= discord.Colour(WHITE)))
                else:
                    await hm.delete()
                    await ctx.send("*Aborted*")
            except asyncio.TimeoutError:
                await hm.delete()
                await ctx.send("*Request Timeout*")
        else:
            await ctx.send(f"__**You haven't start your character, type {get_prefix(ctx.guild.id)}start to begin.**__")

    @commands.command(name= "adventure", aliases=["adv"], pass_context= True)
    async def _adv(self, ctx: commands.Context):
        pass

def setup(bot: commands.Bot):
    bot.add_cog(Adventure(bot))