import discord
import os
import random
import requests
import re
import threading
import asyncio
from discord.ext import commands, tasks
from Settings.MongoManager import MongoManager, new_member_data
from Settings.setting import MONGO_ADDRESS, DB_NAME

WHITE = 0xfffffe

class GuessWord(commands.Cog):

    words: dict = {
        "country":
        [
            'Afghanistan', 'Albania', 'Algeria', 'Andorra', 'Angola', 
            'Antigua', 'Barbuda', 'Argentina', 'Armenia', 'Australia', 'Austria', 'Azerbaijan', 'Bahamas', 'Bahrain', 
            'Bangladesh', 'Barbados', 'Belarus', 'Belgium', 'Belize', 'Benin', 'Bhutan', 'Bolivia', 
            'Bosnia', 'Herzegovina', 'Botswana', 'Brazil', 'Brunei Darussalam', 'Bulgaria', 'Burkina Faso', 'Burundi', 'Cabo Verde', 
            'Cambodia', 'Cameroon', 'Canada', 'Central African Republic', 'Chad', 'Chile', 'China', 
            'Colombia', 'Comoros', 'Congo', 'Cook Islands', 'Costa Rica', 'Croatia', 'Cuba', 'Cyprus', 'Czechia', "Cote d'Ivoire",
            'Congo', 'Denmark', 'Djibouti', 'Dominica', 'Dominican Republic', 'Ecuador', 'Egypt', 
            'El Salvador', 'Equatorial Guinea', 'Eritrea', 'Estonia', 
            'Eswatini', 'Ethiopia', 'Faroe Islands', 'Fiji', 'Finland', 'France', 'Gabon', 
            'Gambia', 'Georgia', 'Germany', 'Ghana', 'Greece', 'Grenada', 'Guatemala', 'Guinea', 'Guinea-Bissau', 'Guyana', 'Haiti', 
            'Honduras', 'Hungary', 'Iceland', 'India', 'Indonesia', 'Iran', 'Iraq', 'Ireland', 
            'Israel', 'Italy', 'Jamaica', 'Japan', 'Jordan', 'Kazakhstan', 'Kenya', 'Kiribati', 'Kuwait', 'Kyrgyzstan', 
            "Laos", 'Latvia', 'Lebanon', 'Lesotho', 'Liberia', 'Libya', 'Lithuania', 'Luxembourg', 
            'Madagascar', 'Malawi', 'Malaysia', 'Maldives', 'Mali', 'Malta', 'Marshall Islands', 'Mauritania', 
            'Mauritius', 'Mexico', 'Micronesia', 'Monaco', 'Mongolia', 'Montenegro', 'Morocco', 
            'Mozambique', 'Myanmar', 'Namibia', 'Nauru', 'Nepal', 'Netherlands', 'New Zealand', 'Nicaragua', 'Niger', 'Nigeria', 'Niue', 
            'North Macedonia', 'Norway', 'Oman', 'Pakistan', 'Palau', 'Panama', 'Papua New Guinea', 
            'Paraguay', 'Peru', 'Philippines', 'Poland', 'Portugal', 'Qatar', 'South Korea', 'North Korea', 'Moldova', 'Romania', 
            'Russia', 'Rwanda', 'Saint Kitts and Nevis', 'Saint Lucia', 'Samoa', 'San Marino', 
            'Saudi Arabia', 'Senegal', 'Serbia', 'Seychelles', 'Sierra Leone', 
            'Singapore', 'Slovakia', 'Slovenia', 'Solomon Islands', 'Somalia', 'South Africa', 
            'South Sudan', 'Spain', 'Sri Lanka', 'Sudan', 'Suriname', 'Sweden', 'Switzerland', 'Syria', 'Tajikistan', 'Thailand', 
            'Timor-Leste', 'Togo', 'Tokelau ', 'Tonga', 'Trinidad', 'Tobago', 'Tunisia', 'Turkey', 
            'Turkmenistan', 'Tuvalu', 'Uganda', 'Ukraine', 'United Arab Emirates', 'United Kingdom', 'Great Britain', 
            'Tanzania', 'United States America', 'Uruguay', 'Uzbekistan', 'Vanuatu', 'Venezuela', 'VietNam', 'Yemen', 'Zambia'
        ],
        "fruit":
        [
            'Apple', 'Apricots', 'Avocado', 'Banana', 'Blackberries', 'Blackcurrant', 'Blueberries', 
            'Breadfruit', 'Cantaloupe', 'Carambola', 'Cherimoya', 'Cherries', 'Clementine', 
            'Coconut', 'Cranberries', 'Custard Apple', 'Date Fruit', 'Dragonfruit', 'Durian', 'Elderberries', 
            'Feijoa', 'Figs', 'Gooseberries', 'Grapefruit', 'Grapes', 'Guava', 'Honeydew Melon', 'Jackfruit', 'Java Plum', 
            'Jujube Fruit', 'Kiwifruit', 'Kumquat', 'Lemon', 'Lime', 'Longan', 'Loquat', 'Lychee', 
            'Mandarin', 'Mango', 'Mangosteen', 'Mulberries', 'Nectarine', 'Olives', 'Orange', 'Papaya', 'Passion Fruit', 
            'Peaches', 'Pear', 'Pineapple', 'Pitanga', 'Plantain', 'Plums', 'Pomegranate', 'Prickly Pear', 
            'Prunes', 'Pummelo', 'Quince', 'Raspberries', 'Rhubarb', 'Rose Apple', 'Sapodilla', 'Sapote Mamey', 
            'Soursop', 'Strawberries', 'Sugar Apple', 'Tamarind', 'Tangerine', 'Watermelon'
        ],
        'animal':
        [
            'Dog', 'Puppy', 'Turtle', 'Rabbit', 'Parrot', 'Cat', 'Kitten', 'Goldfish', 'Mouse', 
            'Fish', 'Hamster', 'Cow', 'Rabbit', 'Ducks', 'Shrimp', 'Pig', 'Goat', 'Crab', 'Deer', 'Bee',
            'Sheep', 'Fish', 'Turkey', 'Dove', 'Chicken', 'Horse', 'Crow', 'Peacock', 'Dove', 'Sparrow', 
            'Goose', 'Stork', 'Pigeon', 'Turkey', 'Hawk', 'Eagle', 'Raven', 'Parrot', 'Flamingo', 'Seagull', 'Ostrich',
            'Swallow', 'Penguin', 'Robin', 'Swan', 'Owl', 'Woodpecker', 'Hummingbird', 'Albatross', 'Vulture', 'Swan'
        ]
    }

    def __init__(self, bot):
        self.bot = bot
        self.mongodbm = MongoManager(MONGO_ADDRESS, DB_NAME)
        self.mongodbm.ConnectCollection("members")

    def random_machine(self, word:str):
        new_str_rnd = ""
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

    def check_answer(self, channel, question, embed : discord.Embed, answer: str):
        # Edit Local Message
        async def edit_local_message():
            wrong = [
                "Wrong!", 
                "Nope.", 
                "Try Again!", 
                "Not the Answer.",
                "Anyone Else?",
                "Guess again!"
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

    # Game Started
    async def scramble_start(self, *, channel: discord.TextChannel, category : str, secret_word : str):
        # Attributes 
        _que = self.random_machine(secret_word.upper())
        _emb = discord.Embed(title="❓ Guess the Word ❓", description=f"Category : **{category}**\n> **{_que}**", colour=discord.Colour(WHITE))
        _emb.set_footer(text="First Come First Serve")
        handler = await channel.send(embed = _emb)
        answered: discord.Message = None

        # Waiting for User Right Answer
        try:
            answered = await self.bot.wait_for(
                event="message", 
                check=self.check_answer(channel, handler, _emb, answer=secret_word), 
                timeout=20
            )
            winner: discord.User = answered.author

            # When the Answer is Right
            reward = random.randint(1, 3)
            _emb = discord.Embed(
                title="◔‿◔ Correct!", 
                description=f"Congratulation : **{winner.name}**.\nReward : **{reward}** coins", 
                colour=discord.Colour(WHITE)
            )
            user_data: dict = self.checkin_member(answered.id)
            user_data["money"] += 10
            self.mongodbm.UpdateOneObject({"member_id": answered.id}, user_data)
            await channel.send(embed = _emb)
            
        except asyncio.TimeoutError:
            # When nobody can answer it
            _emb = discord.Embed(
                title= "ʘ︵ʘ No One Answer", 
                description=f"The answer is **{secret_word}**.", 
                colour=discord.Colour(WHITE)
            )

        await handler.delete()
        await channel.send(embed = _emb)

    def checkin_member(self, person_id: int) -> dict:
        """
        
        Check if Member is in the Database.

            Returns :
                (dict) => Member Information
        
        """
        query: dict = {"member_id":person_id}
        u_data: list = self.mongodbm.FindObject(query)
        if len(u_data) < 1:
            nd: dict = new_member_data
            nd["member_id"] = person_id
            self.mongodbm.InsertOneObject(nd)
            u_data = self.mongodbm.FindObject(query)
        return u_data[0]

    @commands.command(aliases=["scr"])
    async def scramble(self, ctx, *, category: str = 'random'):
        list_of_word : list or tuple
        if category.lower() == 'random':
            category = random.choice(list(self.words))
            list_of_word = self.words[category]
            await self.scramble_start(channel = ctx.message.channel, category = category, secret_word = random.choice(list_of_word))
        else:
            if category not in self.words:
                category = random.choice(list(self.words))
            list_of_word = self.words[category]
            await self.scramble_start(channel = ctx.message.channel, category = category, secret_word = random.choice(list_of_word))

    @commands.command(aliases=["hang"])
    async def hangman(self, ctx):
        pass

def setup(bot):
    bot.add_cog(GuessWord(bot))