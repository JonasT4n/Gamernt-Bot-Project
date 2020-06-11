import discord
from discord.ext import commands
from Settings.MongoManager import MongoManager
from Settings.MyUtility import checkin_guild

class RPGManager(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Event Listener Area

    @commands.Cog.listener()
    async def on_ready(self):
        print("RPG Manager on Duty!")

    # Commands Area

    @commands.command(name= "item", pass_context= True)
    async def _item(self, ctx: commands.Context):
        pass

    @commands.command(name= "create", pass_context= True)
    async def _equip(self, ctx: commands.Context):
        pass

    @commands.command(name= "moves", aliases= ["learned"], pass_context= True)
    async def _learned_moves(self, ctx: commands.Context):
        pass

    @commands.command(name= "skillreset", aliases= ["skillres"], pass_context= True)
    async def _reset_skill(self, ctx: commands.Context):
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