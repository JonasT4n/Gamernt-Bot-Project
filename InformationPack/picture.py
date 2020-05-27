import discord
import sys
import os
from discord.ext import commands

class Picture(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Listener Area

    @commands.Cog.listener()
    async def on_ready(self):
        print("Picture Searcher is Ready!")

    # Command Area

    @commands.command(aliases=["pict", "img"])
    async def picture(self, ctx):
        pass

def setup(bot : commands.Bot):
    bot.add_cog(Picture(bot))