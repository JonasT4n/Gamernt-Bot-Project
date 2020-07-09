import discord
import asyncio
from discord.ext import commands
from Settings.MyUtility import checkin_guild, db_mbr

WHITE = 0xfffffe

class RPGManager(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Commands Area

    @commands.command(name= "item", aliases= ['items'], pass_context= True)
    async def _item(self, ctx: commands.Context):
        pass

    @commands.command(name="equip")
    async def _equip(self, ctx: commands.Context):
        pass

    @commands.command(name="moves", aliases=["learned"])
    async def _learned_moves(self, ctx: commands.Context):
        pass

    @commands.command(name="learn")
    async def _learn(self, ctx: commands.Context):
        pass

    @commands.command(name="make")
    async def _make_things(self, ctx: commands.Context, *args):
        pass

    # Others

def setup(bot: commands.Bot):
    bot.add_cog(RPGManager(bot))