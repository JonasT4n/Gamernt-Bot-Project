import discord
import os
import random
import requests
import re
import threading
import asyncio
from discord.ext import commands, tasks
from Settings.StaticData import words

WHITE = 0xfffffe

class GuessWord(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Listener Area

    @commands.Cog.listener()
    async def on_ready(self):
        print("Guess Word Games is all Ready!")

    # Checker Area

    

    # Command Area

    @commands.command(name= "scramble", aliases= ["scr"], pass_context= True)
    async def _scramble(self, ctx: commands.Context, *, category: str = 'random'):
        list_of_word : list or tuple
        if category.lower() == 'random':
            category = random.choice(list(words))
        else:
            if category not in words:
                category = random.choice(list(words))
        list_of_word = words[category]
        await self.scramble_start(ctx.channel, category, random.choice(list_of_word))

    @commands.command(name= "hangman", aliases= ["hang"], pass_context= True)
    async def _hangman(self, ctx: commands.Context, *, category: str = 'random'):
        list_of_word : list or tuple
        if category.lower() == 'random':
            category = random.choice(list(words))
        else:
            if category not in words:
                category = random.choice(list(words))
        list_of_word = words[category]
        await self.hangman_start(ctx.channel, ctx.author, category, random.choice(list_of_word))

    # Others

    async def hangman_start(self, channel: discord.TextChannel, person: discord.User, category: str, sw: str):
        # inner function
        def check_answer():
            pass

        def hide(word: str) -> list:
            kword: list = []
            for k in word:
                if k == ' ':
                    kword.append(' ')
                else:
                    kword.append('`_`')
            return kword

        # Attribute
        hang_thumbnail: list = []
        hidden_answer: list = hide(sw.upper())
        hanged: bool = False
        alphabet: list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

    async def scramble_start(self, channel: discord.TextChannel, category: str, sw: str):
        # Inner Function
        def check_answer(channel: discord.TextChannel, question: discord.Message, embed : discord.Embed, answer: str):
            async def edit_local_message(person_name: str):
                wrong = [
                    "Wrong!", 
                    "Nope.", 
                    "Try Again!", 
                    "Not the Answer.",
                    "Anyone Else?",
                    "Guess again.",
                    "Unfortunate."
                    ]
                embed.set_footer(text= f"{random.choice(wrong)} | Last reply : {person_name}")
                await question.edit(embed= embed)

            def inner_check(message):
                if message.channel == channel and message.content.lower() == answer.lower():
                    return True
                elif message.channel == channel:
                    asyncio.create_task(edit_local_message(message.author.name))
                    return False
                else:
                    return False
            return inner_check

        def scramble_machine(word: str) -> str:
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

        # Attributes 
        _que: str = scramble_machine(sw.upper())
        _emb = discord.Embed(
            title= "❓ Guess the Word ❓", 
            description= f"Category : **{category}**\n> **{_que}**", 
            colour= discord.Colour(WHITE)
            )
        _emb.set_footer(text= "First Come First Serve")
        handler: discord.Message = await channel.send(embed = _emb)

        # Start Game
        try:
            answered: discord.Message = await self.bot.wait_for(
                event= "message", 
                check= check_answer(channel, handler, _emb, answer= sw), 
                timeout= 20
            )
            _emb = discord.Embed(
                title= "◔‿◔ Correct!", 
                description= f"🏆 Congratulation : **{answered.author.name}**\nAnswer is **{sw}**", 
                colour= discord.Colour(WHITE)
            )
            await channel.send(embed= _emb)
            
        except asyncio.TimeoutError:
            # When nobody can answer it
            _emb = discord.Embed(
                title= "ʘ︵ʘ No One Answer", 
                description=f"The answer is **{sw}**.", 
                colour=discord.Colour(WHITE)
            )
            await handler.delete()
            await channel.send(embed= _emb)

def setup(bot):
    bot.add_cog(GuessWord(bot))