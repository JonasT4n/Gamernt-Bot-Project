import discord
import asyncio
from discord.ext import commands
from Settings.MyUtility import checkin_guild, checkin_member, db_gld, db_mbr

class Shop(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Commands Area

    @commands.command(name="shop")
    async def _open_shop(self, ctx: commands.Context, *args):
        pass

    @commands.command(name="buy")
    async def _buy(self, ctx: commands.Context, *args):
        pass

    # Others

def setup(bot: commands.Bot):
    bot.add_cog(Shop(bot))