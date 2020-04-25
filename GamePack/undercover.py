import discord
from discord.ext import commands

WHITE = 0xfffffe

class Undercover(commands.Cog):

    def __init(self, bot: commands.Bot):
        self.bot = bot

def setup(bot:commands.Bot):
    bot.add_cog(Undercover(bot))