import discord
import os
import random
import requests
import re
import threading
import asyncio
from discord.ext import commands
from Settings.StaticData import words
from Settings.MyUtility import get_prefix

WHITE = 0xfffffe

class GuessWord(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Command Area

    @commands.command(name= "scramble", aliases= ["scr"], pass_context= True)
    async def _scramble(self, ctx: commands.Context, *, category: str = 'random'):
        list_of_word : list or tuple
        if category.lower() == 'random':
            category = random.choice(list(words))
        else:
            categories: list = [i.lower() for i in words]
            if category.lower() not in categories:
                category = random.choice(list(words))
            else:
                category = category.lower()
        list_of_word = words[category.capitalize()]
        await self.scramble_start(ctx.channel, category, random.choice(list_of_word))

    @commands.command(name= "hangman", aliases= ["hang"], pass_context= True)
    async def _hangman(self, ctx: commands.Context, *, category: str = 'random'):
        # Inner Check Function
        def check_reaction_user(message: discord.Message, list_of_joined: list):
            def inner_check(reaction: discord.Reaction, user: discord.User):
                if str(reaction.emoji) == "👋" and user not in list_of_joined:
                    return True
                elif str(reaction.emoji) == "⏭️" and user == list_of_joined[0]:
                    return True
                else:
                    return False 
            return inner_check

        # Get Category
        list_of_word : list or tuple
        players: list = [ctx.author]
        if category.lower() == 'random':
            category = random.choice(list(words))
        else:
            categories: list = [i.lower() for i in words]
            if category.lower() not in categories:
                category = random.choice(list(words))
            else:
                category = category.lower()
        list_of_word = words[category.capitalize()]

        # Queue section
        hm: discord.Message
        try:
            emb = discord.Embed(
                title= "Waiting for Player to Join | 1/5 Slot",
                description= f"> {players[0].name} (Host)",
                colour= discord.Colour(WHITE)
                )
            emb.set_footer(text= "React 👋 to join, and ⏭️ to skip to game if you are a host.")
            hm = await ctx.send(embed= emb)
            await hm.add_reaction("👋")
            await hm.add_reaction("⏭️")
            while True:
                r: discord.Reaction
                u: discord.Message
                r, u = await self.bot.wait_for(
                    event= "reaction_add",
                    check= check_reaction_user(hm, players),
                    timeout= 30.0
                    )
                if str(r.emoji) == "⏭️":
                    raise asyncio.TimeoutError
                else:
                    players.append(u)
                    if len(players) == 5:
                        raise asyncio.TimeoutError

                # Update Joined Player
                desc: list = []
                for j in range(len(players)):
                    if j == 0:
                        desc.append(f"> {players[j].name} (Host)")
                    else:
                        desc.append(f"> {players[j].name}")
                emb = discord.Embed(
                    title= f"Waiting for Player to Join | {len(players)}/5 Slot",
                    description= "\n".join(desc),
                    colour= WHITE
                    )
                emb.set_footer(text= "React 👋 to join, and ⏭️ to skip to game if you are a host.")
                await hm.edit(embed= emb)
        except asyncio.TimeoutError:
            await hm.delete(delay= 1)
            await self.hangman_start(ctx.channel, players, category, random.choice(list_of_word))

    @commands.command(name= "wordpref", aliases= ['wop'], pass_context= True)
    async def _wpref(self, ctx: commands.Context, *, category: str = "Everyword"):
        # Inner Check
        def check_queue(ppl: list):
            def inner_check(reaction: discord.Reaction, user: discord.User):
                if str(reaction.emoji) == "👋" and user not in ppl:
                    return True
                elif str(reaction.emoji) == "⏭️" and user == ppl[0]:
                    return True
                else:
                    return False 
            return inner_check

        # Send Hint
        menus: list = ["👋", "⏭️"]
        players: list = [ctx.author]
        emb = discord.Embed(
            title= "🧸 Word Prefix | Queue",
            description= f"You need at least 2 players to play this game. Category : __**{category}**__\n"
                f"> {players[0].name} (Host)",
            colour= WHITE
            )
        emb.set_footer(text= "React 👋 to enter, and ⏭️ to play game if you are a host.")
        hm: discord.Message = await ctx.send(embed= emb)
        for i in menus:
            await hm.add_reaction(i)

        # Wait for Reactions
        try:
            while True:
                r: discord.Reaction
                u: discord.User
                r, u = await self.bot.wait_for(
                    event= "reaction_add",
                    check= check_queue(players),
                    timeout= 30.0
                    )

                # Check Reaction
                if str(r.emoji) == "⏭️":
                    break
                else:
                    players.append(u)
                    if len(players) >= 10:
                        break

                # Edit Hint
                desc: str = f"You need at least 2 players to play this game. Category : __{category}__\n"
                for j in range(len(players)):
                    if j == 0:
                        desc += f"> {players[j].name} (Host)\n"
                    elif j == len(players) - 1:
                        desc += f"> {players[j].name}"
                    else:
                        desc += f"> {players[j].name}\n"
                emb = discord.Embed(
                    title= "🧸 Word Prefix | Queue",
                    description= desc,
                    colour= WHITE
                    )
                emb.set_footer(text= "React 👋 to enter, and ⏭️ to play game if you are a host.")
                await r.remove(u)
                await hm.edit(embed= emb)
            
            # Start
            await hm.delete()
            await self.wpref_start(ctx.channel, category, players)

        except asyncio.TimeoutError:
            await hm.delete(delay= 1)
            await ctx.send("*Request Timeout. Game Aborted!*")

    # Games Start

    async def hangman_start(self, channel: discord.TextChannel, persons: list, category: str, sw: str):
        # inner function
        def hide(word: str) -> list:
            kword: list = []
            for k in word:
                if k == ' ':
                    kword.append(' ')
                else:
                    kword.append('_')
            return kword

        def is_char(word: str):
            w: list = len(word.split(' '))
            if len(w) > 1:
                return False
            return True if len(w[0]) == 1 else False

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
            title="웃 Hangman",
            description=f"Category : **{category}**\n"
                f"`{''.join(hidden_answer)}`",
            colour=WHITE
            )
        emb.add_field(
            name="List of unused word :",
            value=f"> {'|'.join(alphabet)}",
            inline=False
            )
        emb.set_thumbnail(url=hang_thumbnail[index])
        emb.set_footer(text="Send a single word until it revealed the answer")
        emb.set_author(
            name=persons[0].name,
            icon_url=persons[0].avatar_url
            )
        hm: discord.Message = await channel.send(embed=emb)
        try:
            turn_index: int = 0
            turn: discord.User = persons[turn_index]
            while True:
                reply: discord.Message = await self.bot.wait_for(
                    event="message",
                    check=lambda message: True if message.channel == channel and message.author == turn 
                        and is_char(message.content) else False,
                    timeout=30.0
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

                # Edit Current Hint
                turn_index = (turn_index+1) if turn_index < len(persons) - 1 else 0
                emb = discord.Embed(
                    title="웃 Hangman",
                    description=f"Category : **{category}**\n"
                        f"`{''.join(hidden_answer)}`",
                    colour=WHITE
                    )
                emb.add_field(
                    name="List of unused word :",
                    value=f"> {'|'.join(alphabet)}",
                    inline=False
                    )
                emb.set_thumbnail(url= hang_thumbnail[index])
                emb.set_author(
                    name=persons[turn_index].name,
                    icon_url=persons[turn_index].avatar_url
                    )
                if ''.join(hidden_answer) == sw.upper():
                    emb.set_footer(text="You WIN! 👍")
                    await hm.edit(embed=emb)
                    break
                else:
                    if penalty is True:
                        if index == len(hang_thumbnail) - 1:
                            emb.set_footer(text="You Lose! 👎")
                            await hm.edit(embed=emb)
                            break
                        emb.set_footer(text="Word not in the Secret Word")
                    else:
                        emb.set_footer(text="Found one! Send more word")
                    await hm.edit(embed=emb)
        except asyncio.TimeoutError:
            await hm.delete()
            await channel.send("*Game Timeout!*")

    async def scramble_start(self, channel: discord.TextChannel, category: str, sw: str):
        # Inner Function
        def check_answer(channel: discord.TextChannel, question: discord.Message, embed : discord.Embed, answer: str):
            async def edit_local_message(person_name: str):
                wrong = [
                    "Wrong!", 
                    "Oof, Nope.", 
                    "Try Again!", 
                    "Not the Answer.",
                    "Anyone Else?",
                    "Guess again.",
                    "Unfortunate.",
                    "Come On, Men!"
                    ]
                embed.set_footer(text=f"{random.choice(wrong)} | Last reply : {person_name}")
                await question.edit(embed=embed)

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
            new_str_rnd: str = word
            splitted_words: list = word.split(' ')
            while True:
                if word != new_str_rnd:
                    break
                else:
                    new_str_rnd = ""
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
        hm: discord.Message = await channel.send(embed= discord.Embed(title= 'Ready?', colour= discord.Colour(WHITE)))
        for j in range(3, 0, -1):
            await hm.edit(embed= discord.Embed(title= f'{j}', colour= discord.Colour(WHITE)))
            await asyncio.sleep(1)
        _que: str = scramble_machine(sw.upper())
        _emb = discord.Embed(
            title= "❓ Guess the Word ❓", 
            description= f"> Category : **{category}**\n"
                f"> **{_que}**", 
            colour= discord.Colour(WHITE)
            )
        _emb.set_footer(text= "First Come First Serve")
        await hm.edit(embed= _emb)

        # Start Game
        try:
            answered: discord.Message = await self.bot.wait_for(
                event= "message", 
                check= check_answer(channel, hm, _emb, answer= sw), 
                timeout= 20
                )
            _emb = discord.Embed(
                title= "◔‿◔ Correct!", 
                description= f"🏆 Congratulation : **{answered.author.name}**\n"
                    f"Answer is **{sw}**", 
                colour= discord.Colour(WHITE)
                )
            await hm.delete()
            await channel.send(embed= _emb)
            
        except asyncio.TimeoutError:
            # When nobody can answer it
            _emb = discord.Embed(
                title= "ʘ︵ʘ No One Answer", 
                description=f"The answer is **{sw}**.", 
                colour=discord.Colour(WHITE)
                )
            await hm.delete()
            await channel.send(embed= _emb)

    async def wpref_start(self, channel: discord.TextChannel, category: str, players: list):
        # Inner Check
        def check_startwith(letter: str, guessed: str):
            return True if guessed.startswith(letter) else False

        def check_reply(onmsg: discord.Message):
            async def edit_msg(word: str):
                desc: str = f"Category: __{category}__ | Start With: **{_startwith}**\n"
                for ppls in range(len(guessed_player)):
                    if ppls == 0:
                        desc += f"> {guessed_player[ppls][0].name} => **{guessed_player[ppls][1]}**"
                    else:
                        desc += f"\n> {guessed_player[ppls][0].name} => **{guessed_player[ppls][1]}**"
                desc += "\n"
                for ppls in range(len(players)):
                    if ppls == 0:
                        desc += f"> {players[ppls].name} => *Not Send Yet*"
                    else:
                        desc += f"\n> {players[ppls].name} => *Not Send Yet*"
                emb = discord.Embed(
                    title= f"🧸 Word Prefix",
                    description= desc,
                    colour= WHITE
                    )
                emb.set_footer(text= "Just send a single word message in this channel.")
                await onmsg.edit(embed= emb)

            def inner_check(message: discord.Message):
                word_sent: str = message.content
                if check_startwith(_startwith, word_sent) and len(word_sent.split(' ')) == 1 and message.author in players:
                    guessed_player.append((message.author, word_sent))
                    players.remove(message.author)
                    asyncio.create_task(message.delete())
                    if len(guessed_player) == _len_players:
                        return True
                    asyncio.create_task(edit_msg(word_sent))
                return False
            return inner_check

        # Initialize Attribute and Send Hint
        alphabet: list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        guessed_player: list = []
        _len_players = len(players)
        _startwith: str = random.choice(alphabet)
        desc: str = f"Category: __{category}__ | Start With: **{_startwith}**\n"
        for ppls in range(len(players)):
            if ppls == 0:
                desc += f"> {players[ppls].name} => *Not Send Yet*"
            else:
                desc += f"\n> {players[ppls].name} => *Not Send Yet*"
        emb = discord.Embed(
            title=f"🧸 Word Prefix",
            description=desc,
            colour=WHITE
            )
        emb.set_footer(text= "Just send a single word message in this channel.")
        hm: discord.Message = await channel.send(embed=emb)

        try:
            # Wait all Answer
            msg: discord.Message = await self.bot.wait_for(
                event="message",
                check=check_reply(hm),
                timeout=30.0
                )
            await hm.delete()

            # Result
            desc: str = f"Category: __{category}__ | Start With: **{_startwith}**\n"
            for res in range(len(guessed_player)):
                if res == len(guessed_player) - 1:
                    desc += f"> {guessed_player[res][0].name} => **{guessed_player[res][1]}**"
                else:
                    desc += f"> {guessed_player[res][0].name} => **{guessed_player[res][1]}**\n"
            emb = discord.Embed(
                title=f"🧸 Word Prefix",
                description=desc,
                colour=WHITE
                )
            emb.set_footer(text="All Player has given their word. Result!")
            await channel.send(embed=emb)
        except asyncio.TimeoutError:
            # Result
            desc: str = f"Category: __{category}__ | Start With: **{_startwith}**\n"
            for k in range(len(guessed_player)):
                if k == 0:
                    desc += f"> {guessed_player[k][0].name} => **{guessed_player[k][1]}**"
                else:
                    desc += f"\n> {guessed_player[k][0].name} => **{guessed_player[k][1]}**"
            desc += "\n"
            for k in range(len(players)):
                if k == 0:
                    desc += f"> {players[k].name} => *NULL*"
                else:
                    desc += f"\n> {players[k].name} => *NULL*"
            emb = discord.Embed(
                title=f"🧸 Word Prefix",
                description=desc,
                colour=WHITE
                )
            emb.set_footer(text="Time is Up! Result!")
            await hm.edit(embed=emb)

def setup(bot: commands.Bot):
    bot.add_cog(GuessWord(bot))