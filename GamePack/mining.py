import discord
import asyncio
import random
from discord.ext import commands

WHITE = 0xfffffe

class Mine(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(aliases=['mining'])
    async def mine(self, ctx):
        dig = "Dig... "

        # List of Ores
        ores = ["Copper", "Lead", "Tin", 
        "Cobalt", "Iron", "Coal", 
        "Silver", "Ruby", "Sapphire", 
        "Gold", "Diamond", "Emerald", 
        "Titanium", "Meteorite", "Plastanium"]

        emb = discord.Embed(title="⛏️ Mining...", description=dig, colour=discord.Colour(WHITE))
        queing = await ctx.send(embed=emb)
        await asyncio.sleep(0.5)
        for i in range(2):
            dig += "Dig... "
            emb = discord.Embed(title="⛏️ Mining...", description=dig, colour=discord.Colour(WHITE))
            await queing.edit(embed=emb)
            await asyncio.sleep(0.5)
        emb = discord.Embed(title="💎 Bling!", description="You Got **{}**!".format(random.choice(ores)), colour=discord.Colour(WHITE))
        await queing.edit(embed = emb)

    @commands.command()
    async def ores(self, ctx):
        pass

def setup(bot):
    bot.add_cog(Mine(bot))