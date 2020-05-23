import discord
import random
import asyncio
import threading
from discord.ext import commands
from Settings.MyUtility import checkin_member
from Settings.MongoManager import MongoManager, new_member_data

WHITE = 0xfffffe

class Player:

    _on_hand: list = []

    def __init__(self, person: discord.User):
        self._player = person
    
    @property
    def player(self):
        return self._player
    
    @player.setter
    def player(self, person: discord.User):
        self._player = person

    @property
    def on_hand(self):
        return self._on_hand

    @on_hand.setter
    def on_hand(self, save_list: list):
        self._on_hand = save_list

    def draw_card(self, which_card: str):
        pass

    def take_card(self):
        pass

class Cards(commands.Cog):

    identified_deck: dict = {
        "spade":["A♤", "2♤", "3♤", "4♤", "5♤", "6♤", "7♤", "8♤", "9♤", "10♤", "J♤", "Q♤", "K♤"],
        "heart":["A♡", "2♡", "3♡", "4♡", "5♡", "6♡", "7♡", "8♡", "9♡", "10♡", "J♡", "Q♡", "K♡"],
        "club":["A♧", "2♧", "3♧", "4♧", "5♧", "6♧", "7♧", "8♧", "9♧", "10♧", "J♧", "Q♧", "K♧"],
        "diamond":["A♢", "2♢", "3♢", "4♢", "5♢", "6♢", "7♢", "8♢", "9♢", "10♢", "J♢", "Q♢", "K♢"]
    }

    overflow_deck: list = [
        "A♤", "2♤", "3♤", "4♤", "5♤", "6♤", "7♤", "8♤", "9♤", "10♤", "J♤", "Q♤", "K♤", 
        "A♡", "2♡", "3♡", "4♡", "5♡", "6♡", "7♡", "8♡", "9♡", "10♡", "J♡", "Q♡", "K♡", 
        "A♧", "2♧", "3♧", "4♧", "5♧", "6♧", "7♧", "8♧", "9♧", "10♧", "J♧", "Q♧", "K♧",
        "A♢", "2♢", "3♢", "4♢", "5♢", "6♢", "7♢", "8♢", "9♢", "10♢", "J♢", "Q♢", "K♢"
    ]

    board_template: dict = {
        "blackjack": discord.Embed(
            title = "🂡 Blackjack",
            colour = discord.Colour(WHITE)
        )
    }

    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.mongodbm = MongoManager(collection="members")

    async def challange_bot(self, p: Player):
        board_embed: discord.Embed = self.board_template["blackjack"]

    # Listener Area

    @commands.Cog.listener()
    async def on_ready(self):
        print("Card Game Ready!")

    # Checker Area

    # Command Area

    @commands.command()
    async def blackjack(self, ctx: commands.Context, *, challange: discord.User = None):
        if challange is None:
            await self.challange_bot(Player(ctx.author))
        else:
            pass

    # Others

def setup(bot:commands.Bot):
    bot.add_cog(Cards(bot))