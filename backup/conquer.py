import discord
import requests
import re
from discord.ext import commands

class Conquer(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def help_survival(self, ctx):
        pass

    @commands.command(aliases=["conq"])
    async def conquer(self, ctx):
        pass

def setup(bot):
    bot.add_cog(Conquer(bot))