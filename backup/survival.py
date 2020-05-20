import discord
import asyncio
import threading
from discord.ext import commands

WHITE = 0xfffffe

class Survival(commands.Cog):

    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @commands.command(aliases=['surv'])
    async def survival(self, ctx, stat: str):
        pass

def setup(bot:commands.Bot):
    bot.add_cog(Survival(bot))