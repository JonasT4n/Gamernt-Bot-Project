import discord
import os
import random
import requests
import re
import threading
import asyncio
from discord.ext import commands
from Settings.StaticData import words

WHITE = 0xfffffe

class GuessWord(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Listener Area

    @commands.Cog.listener()
    async def on_ready(self):
        print("Guess Word Games is all Ready!")

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
        def hide(word: str) -> list:
            kword: list = []
            for k in word:
                if k == ' ':
                    kword.append(' ')
                else:
                    kword.append('_')
            return kword

        # Attribute
        hang_thumbnail: list = [
            "https://trello-attachments.s3.amazonaws.com/5ee1ce776c251b35623336e8/240x240/191e849e296dcd07972114b2facd43ad/Hangman_0.png",
            "https://trello-attachments.s3.amazonaws.com/5ee1ce776c251b35623336e8/240x240/30777b2d67002187ff97ac8097435823/Hangman_1.png",
            "https://trello-attachments.s3.amazonaws.com/5ee1ce776c251b35623336e8/240x240/88b6abb14e76fe3e8e87ae6509e10d94/Hangman_2.png",
            "https://trello-attachments.s3.amazonaws.com/5ee1ce776c251b35623336e8/240x240/0f732133f671cbbe803ffc76637bb3fd/Hangman_3.png",
            "https://trello-attachments.s3.amazonaws.com/5ee1ce776c251b35623336e8/240x240/2b4ca13e066435b2bc9429aaf9f4f9c0/Hangman_4.png",
            "https://trello-attachments.s3.amazonaws.com/5ee1ce776c251b35623336e8/240x240/e0d64e4631bc7d262457439896f9ca22/Hangman_5.png",
            "https://trello-attachments.s3.amazonaws.com/5ee1ce776c251b35623336e8/240x240/f86523f7d448f8d1d88d81c8e41cf15a/Hangman_6.png"
            ]
        hidden_answer: list = hide(sw.upper())
        alphabet: list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        index: int = 0
        penalty: bool

        # Gameplay
        emb = discord.Embed(
            title= "웃 Hangman",
            description= f"Category : **{category}**\n"
                f"`{''.join(hidden_answer)}`\n\n"
                f"List of unused word : ```{'|'.join(alphabet)}```",
            colour= discord.Colour(WHITE)
            )
        emb.set_thumbnail(url= hang_thumbnail[index])
        emb.set_footer(text= "Send a single word until it revealed the answer")
        emb.set_author(
            name= person.name,
            icon_url= person.avatar_url
            )
        hm: discord.Message = await channel.send(embed= emb)
        try:
            while True:
                reply: discord.Message = await self.bot.wait_for(
                    event= "message",
                    check= lambda message: True if message.channel == channel and message.author == person and len(message.content.split(' ')[0]) == 1 else False,
                    timeout= 30.0
                    )

                # Check Reply
                penalty = True
                char_rep: str = reply.content.upper()
                sw_up: str = sw.upper()
                if char_rep in alphabet:
                    alphabet.remove(char_rep)
                    if char_rep in sw_up:
                        penalty = False
                        for j in range(len(sw_up)):
                            if char_rep == sw_up[j]:
                                hidden_answer[j] = char_rep
                if penalty is True:
                    index += 1
                await reply.delete()

                # Edit Current
                emb = discord.Embed(
                    title= "웃 Hangman",
                    description= f"Category : **{category}**\n"
                        f"`{''.join(hidden_answer)}`\n\n"
                        f"List of unused word : ```{'|'.join(alphabet)}```",
                    colour= discord.Colour(WHITE)
                    )
                emb.set_thumbnail(url= hang_thumbnail[index])
                emb.set_author(
                    name= person.name,
                    icon_url= person.avatar_url
                    )
                if ''.join(hidden_answer) == sw.upper():
                    emb.set_footer(text= "You WIN! 👍")
                    await hm.edit(embed= emb)
                    break
                else:
                    if penalty is True:
                        emb.set_footer(text= "Word not in the Secret Word")
                    else:
                        emb.set_footer(text= "Found one! Send more word")
                    await hm.edit(embed= emb)
        except asyncio.TimeoutError:
            await hm.delete()
            await channel.send("*Game Timeout!*")

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

def setup(bot: commands.Bot):
    bot.add_cog(GuessWord(bot))