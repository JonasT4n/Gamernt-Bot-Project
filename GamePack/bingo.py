import discord
from discord.ext import commands, tasks
import os, asyncio, threading

WHITE = 0xfffffe

class Bingo(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def bingo(self, ctx, stat: str):
        statuses = ["start", "help", 'h', 'how']
        try:
            if stat.lower() not in statuses:
                raise commands.BadArgument
            
            if stat.lower() == 'start': # Idle Game Start
                raise commands.BadArgument
            
            if stat.lower() == 'help' or stat.lower() == 'h': # Help about Bingo
                raise commands.BadArgument
            
            if stat.lower() == 'how': # How to Play
                raise commands.BadArgument
            
        except Exception as exc:
            if type(exc) == commands.BadArgument:
                await ctx.message.delete()
                emb = discord.Embed(title="BINGO!!!", description="```The Building is Under Construction... Coming Soon!```", colour=discord.Colour(WHITE))
                tempMsg = await ctx.send(embed=emb)
                await asyncio.sleep(5)
                await tempMsg.delete()
            else:
                print(type(exc), exc)
                
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