import discord
from discord.ext import commands, tasks
import os, asyncio, threading

class Duel(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def duel(self, ctx, person1 = None, person2 = None):
        pass
    
    @duel.error
    async def duel_error(self, ctx, error):
        pass
    
def setup(bot):
    bot.add_cog(Duel(bot))