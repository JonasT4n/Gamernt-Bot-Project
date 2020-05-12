import discord
import random
import asyncio
from discord.ext import commands

WHITE = 0xfffffe

class Dice(commands.Cog):

    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Dice Game is Ready!")

    async def dice_help(self, ctx):
        emb = discord.Embed(title="🎲 Invalid Numbers", description="```g.dice <amount> <dots>\nAmount of Dice : 1 - 100\nDots on Dice : 1 - 100```", colour=discord.Colour(WHITE))
        emb.set_footer(text="Ex : g.dice 2 6")
        await ctx.send(embed = emb)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def dice(self, ctx, amount: int = 2, dots: int = 6):
        if amount <= 0 or dots <= 0 or amount > 100 or dots > 100:
            await self.dice_help(ctx)
        else:
            rolled: int = random.randint(1, amount * dots)
            emb = discord.Embed(title="🎲 Dice Rolled", description=f"You Got : **{rolled}**", colour=discord.Colour(WHITE))
            await ctx.send(embed = emb)
        
def setup(bot:commands.Bot):
    bot.add_cog(Dice(bot))