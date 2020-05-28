import discord
import os
import random
import requests
import re
import threading
import asyncio
from discord.ext import commands, tasks
from Settings.MongoManager import MongoManager
from Settings.MyUtility import checkin_member
from Settings.StaticData import words

WHITE = 0xfffffe

class GuessWord(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.mongodbm = MongoManager(collection="members")

    # Listener Area

    @commands.Cog.listener()
    async def on_ready(self):
        print("Guess Word Games is all Ready!")

    # Checker Area

    def check_answer(self, channel: discord.TextChannel, question, embed : discord.Embed, answer: str):
        # Edit Local Message
        async def edit_local_message():
            wrong = [
                "Wrong!", 
                "Nope.", 
                "Try Again!", 
                "Not the Answer.",
                "Anyone Else?",
                "Guess again.",
                "Unfortunate."
            ]
            embed.set_footer(text=random.choice(wrong))
            await question.edit(embed = embed)
            
        # Check Inner
        def inner_check(message):
            if message.channel == channel and message.content.lower() == answer.lower():
                return True
            elif message.channel == channel:
                asyncio.create_task(edit_local_message())
                return False
            else:
                return False
        return inner_check

    # Command Area

    @commands.command(aliases=["scr"])
    async def scramble(self, ctx, *, category: str = 'random'):
        list_of_word : list or tuple
        if category.lower() == 'random':
            category = random.choice(list(words))
            list_of_word = words[category]
            await self.scramble_start(ctx.message.channel, category, random.choice(list_of_word))
        else:
            if category not in words:
                category = random.choice(list(words))
            list_of_word = words[category]
            await self.scramble_start(ctx.message.channel, category, random.choice(list_of_word))

    @commands.command(aliases=["hang"])
    async def hangman(self, ctx):
        pass

    # Others

    async def scramble_start(self, channel: discord.TextChannel, category : str, secret_word : str):
        # Attributes 
        _que = self.random_machine(secret_word.upper())
        _emb = discord.Embed(title="❓ Guess the Word ❓", description=f"Category : **{category}**\n> **{_que}**", colour=discord.Colour(WHITE))
        _emb.set_footer(text="First Come First Serve")
        handler = await channel.send(embed = _emb)
        answered: discord.Message = None

        # Waiting for User Right Answer
        try:
            answered: discord.Message = await self.bot.wait_for(
                event="message", 
                check=self.check_answer(channel, handler, _emb, answer=secret_word), 
                timeout=20
            )
            winner: discord.User = answered.author

            # When the Answer is Right
            _emb = discord.Embed(
                title="◔‿◔ Correct!", 
                description=f"🏆 Congratulation : **{winner.name}**\nAnswer is **{secret_word}**", 
                colour=discord.Colour(WHITE)
            )
            await channel.send(embed = _emb)
            self.mongodbm.IncreaseItem({"member_id": str(answered.author.id)}, {"trophy": 1}) # Save Data
            
        except asyncio.TimeoutError:
            # When nobody can answer it
            _emb = discord.Embed(
                title= "ʘ︵ʘ No One Answer", 
                description=f"The answer is **{secret_word}**.", 
                colour=discord.Colour(WHITE)
            )
            await handler.delete()
            await channel.send(embed = _emb)

    @staticmethod
    def random_machine(word: str) -> str:
        new_str_rnd: str = ""
        splitted_words: list = word.split(' ')
        for i in range(len(splitted_words)):
            if i == len(splitted_words) - 1:
                while len(splitted_words[i]) > 0:
                    index_random = random.randint(0, len(splitted_words[i]) - 1)
                    new_str_rnd += splitted_words[i][index_random]
                    splitted_words[i] = splitted_words[i][:index_random] + splitted_words[i][index_random + 1:]
            else:
                while len(splitted_words[i]) > 0:
                    index_random = random.randint(0, len(splitted_words[i]) - 1)
                    new_str_rnd += splitted_words[i][index_random]
                    splitted_words[i] = splitted_words[i][:index_random] + splitted_words[i][index_random + 1:]
                new_str_rnd += ' '
        return new_str_rnd

def setup(bot):
    bot.add_cog(GuessWord(bot))