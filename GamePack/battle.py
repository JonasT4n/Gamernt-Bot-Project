import discord
from discord.ext import commands
from Settings.MongoManager import MongoManager
from Settings.MyUtility import checkin_member

class Battle(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.mongodbm = MongoManager(collection="members")

    # Listener Area

    @commands.Cog.listener()
    async def on_ready(self):
        print("Battle RPG System is Ready!")

    # Command Area

    @commands.command()
    async def battle(self, ctx: commands.Context, *args):
        pass

def setup(bot: commands.Bot):
    bot.add_cog(Battle(bot))