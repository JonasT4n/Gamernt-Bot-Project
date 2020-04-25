import discord
import random
from discord.ext import commands

WHITE = 0xfffffe

class Chance(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def chance(self, ctx, *, statement: str):
        emb = discord.Embed(title=f"⭐ Chance of Everything", description=f"\"{statement}\"\nThe Chance is **{random.randint(0, 100)}%**", colour=discord.Colour(WHITE))
        await ctx.send(embed=emb)

    @commands.command(aliases=['ask'])
    async def poolask(self, ctx, *, statement: str):
        reply = [
            "Yes!",
            "No!",
            "Perhaps.",
            "Definitely.",
            "Ofcourse."]
        emb = discord.Embed(title=f"🦉 You ask for it.", description=f"{ctx.message.author.name} : {statement}\nMe : **{random.choice(reply)}**", colour=discord.Colour(WHITE))
        await ctx.send(embed = emb)

def setup(bot):
    bot.add_cog(Chance(bot))