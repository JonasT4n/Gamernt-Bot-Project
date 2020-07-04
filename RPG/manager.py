import discord
import asyncio
from discord.ext import commands
from Settings.MongoManager import MongoManager
from Settings.MyUtility import checkin_guild

WHITE = 0xfffffe

class RPGManager(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.mdb = MongoManager(collection= "members")

    # Commands Area

    @commands.command(name= "item", aliases= ['items'], pass_context= True)
    async def _item(self, ctx: commands.Context):
        pass

    @commands.command(name= "equip", pass_context= True)
    async def _equip(self, ctx: commands.Context):
        pass

    @commands.command(name= "moves", aliases= ["learned"], pass_context= True)
    async def _learned_moves(self, ctx: commands.Context):
        pass

    @commands.command(name= "learn", pass_context= True)
    async def _learn(self, ctx: commands.Context):
        pass

    @commands.command(name= "make", pass_context= True)
    async def _make_things(self, ctx: commands.Context, *args):
        pass

    # Others

def setup(bot: commands.Bot):
    bot.add_cog(RPGManager(bot))