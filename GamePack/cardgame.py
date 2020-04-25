import discord
from discord.ext import commands

WHITE = 0xfffffe

class Cards(commands.Cog):

    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @commands.command()
    async def blackjack(self, ctx):
        pass

def setup(bot:commands.Bot):
    bot.add_cog(Cards(bot))