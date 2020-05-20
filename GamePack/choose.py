import discord
import random
from discord.ext import commands

WHITE = 0xfffffe

class Choose(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Choosing System is Ready!")

    @commands.command()
    async def choose(self, ctx, *obj):
        if len(obj) == 0:
            await ctx.send("You must Insert the Items.\nExample : `g.choose Blue Red Green`")
        else:
            choosen: str = random.choice(obj)
            emb = discord.Embed(title="I Choose",
            description=f"**{choosen}**",
            colour=discord.Colour(WHITE))
            await ctx.send(embed=emb)

def setup(bot):
    bot.add_cog(Choose(bot))