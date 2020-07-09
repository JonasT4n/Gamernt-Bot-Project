import discord
import random
from discord.ext import commands
from Settings.MongoManager import MongoManager
from Settings.MyUtility import checkin_guild, db_mbr

WHITE = 0xfffffe

class Roulette(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Command Section

    @commands.command(name="roulette", aliases=['rlt'])
    @commands.cooldown(1, 60, commands.BucketType.guild)
    async def _roulette(self, ctx: commands.Context, bet: int):
        pass

def setup(bot: commands.Bot):
    bot.add_cog(Roulette(bot))