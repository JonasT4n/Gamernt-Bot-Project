import discord
from discord.ext import commands, tasks
import os, asyncio, threading

WHITE = 0xfffffe

class Bingo(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        
    async def help_bingo(self, ctx):
        emb = discord.Embed(title="BINGO!!!", description="```The Building is Under Construction... Coming Soon!```", colour=discord.Colour(WHITE))
        await ctx.send(embed=emb)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Bingo Ready!")
    
    @commands.command()
    async def bingo(self, ctx, stat: str):
        statuses = ["start", "help", 'h', 'how']
        if stat.lower() not in statuses:
            await self.help_bingo(ctx)
        
        if stat.lower() == 'start': # Idle Game Start
            await self.help_bingo(ctx)
        
        if stat.lower() == 'help' or stat.lower() == 'h': # Help about Bingo
            await self.help_bingo(ctx)
        
        if stat.lower() == 'how': # How to Play
            await self.help_bingo(ctx)
                
    @bingo.error
    async def bingo_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.message.delete()
            emb = discord.Embed(title="BINGO!!!", description="```The Building is Under Construction... Coming Soon!```", colour=discord.Colour(WHITE))
            tempMsg = await ctx.send(embed=emb)
            await asyncio.sleep(5)
            await tempMsg.delete()

def setup(bot):
    bot.add_cog(Bingo(bot))