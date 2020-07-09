import discord
import random
from discord.ext import commands

WHITE = 0xfffffe

class Choose(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Command Area

    @commands.command(name="choose")
    async def choose(self, ctx: commands.Context, *obj):
        if len(obj) == 0:
            await ctx.send("You must Insert the Items.\nExample : `g.choose Blue Red Green`")
        else:
            async with ctx.typing():
                choosen: str = random.choice(obj)
                emb = discord.Embed(title=f"I Choose {choosen}!", colour=WHITE)
            await ctx.send(embed=emb)

def setup(bot: commands.Bot):
    bot.add_cog(Choose(bot))