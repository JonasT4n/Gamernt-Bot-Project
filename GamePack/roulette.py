import discord
import random
from discord.ext import commands

WHITE = 0xfffffe

class Roulette(commands.Cog):

    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @commands.command(aliases=['rlt'])
    @commands.cooldown(1, 30, commands.BucketType.guild)
    async def roulette(self, ctx, bet: int, on: str):
        pass

def setup(bot:commands.Bot):
    bot.add_cog(Roulette(bot))