import discord
import random
from discord.ext import commands

WHITE = 0xfffffe

class Cards(commands.Cog):

    identified_deck: dict = {
        "spade":["A♤", "2♤", "3♤", "4♤", "5♤", "6♤", "7♤", "8♤", "9♤", "10♤", "J♤", "Q♤", "K♤"],
        "heart":["A♡", "2♡", "3♡", "4♡", "5♡", "6♡", "7♡", "8♡", "9♡", "10♡", "J♡", "Q♡", "K♡"],
        "club":["A♧", "2♧", "3♧", "4♧", "5♧", "6♧", "7♧", "8♧", "9♧", "10♧", "J♧", "Q♧", "K♧"],
        "diamond":["A♢", "2♢", "3♢", "4♢", "5♢", "6♢", "7♢", "8♢", "9♢", "10♢", "J♢", "Q♢", "K♢"]
    }
    overflow_deck: list or tuple = [
        "A♤", "2♤", "3♤", "4♤", "5♤", "6♤", "7♤", "8♤", "9♤", "10♤", "J♤", "Q♤", "K♤", 
        "A♡", "2♡", "3♡", "4♡", "5♡", "6♡", "7♡", "8♡", "9♡", "10♡", "J♡", "Q♡", "K♡", 
        "A♧", "2♧", "3♧", "4♧", "5♧", "6♧", "7♧", "8♧", "9♧", "10♧", "J♧", "Q♧", "K♧",
        "A♢", "2♢", "3♢", "4♢", "5♢", "6♢", "7♢", "8♢", "9♢", "10♢", "J♢", "Q♢", "K♢"
    ]

    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Card Game Ready!")

    @commands.command()
    async def drawcard(self, ctx):
        emb = discord.Embed(title=f"You have Drawn {random.choice(self.overflow_deck)}", colour=discord.Colour(WHITE))
        await ctx.send(embed=emb)

    @commands.command()
    async def blackjack(self, ctx):
        pass

def setup(bot:commands.Bot):
    bot.add_cog(Cards(bot))