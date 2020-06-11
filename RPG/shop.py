import discord
from discord.ext import commands
from Settings.MongoManager import MongoManager
from Settings.MyUtility import checkin_guild, checkin_member

class Shop(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.gdb = MongoManager(collection= "guilds")
        self.mdb = MongoManager(collection= "members")

    # Event Listener Area

    @commands.Cog.listener()
    async def on_ready(self):
        print("Meta Shop is Ready!")

    # Commands Area

    @commands.command(name= "shop", pass_context= True)
    async def _open_shop(self, ctx: commands.Context, *args):
        pass

    @commands.command(name= "buy", pass_context= True)
    async def _buy(self, ctx: commands.Context, *args):
        pass

    # Others

def setup(bot: commands.Bot):
    bot.add_cog(Shop(bot))