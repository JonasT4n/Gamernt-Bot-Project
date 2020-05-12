import discord
import asyncio
import random
from discord.ext import commands
from Settings.MongoManager import MongoManager, new_member_data
from Settings.setting import MONGO_ADDRESS, DB_NAME

WHITE = 0xfffffe

class Mine(commands.Cog):

    # List of Ores
    kind_ores: dict = {
        "Copper": 2500,
        "Lead": 1200,
        "Tin": 800,
        "Coal": 500,
        "Iron": 300,
        "Cobalt": 250,
        "Quartz": 200,
        "Silver": 120,
        "Gold": 100,
        "Sapphire": 85,
        "Ruby": 75,
        "Diamond": 30,
        "Emerald": 20,
        "Titanium": 10,
        "Meteorite": 5
    }

    pickaxe_identity: dict = {
        0: {
            "name": "Stone Pickaxe"
        },

        1: {
            "name": "Copper Pickaxe",
            "requirement": {
                "Copper": 15,
                "Lead": 10,
                "Tin": 8,
                "Iron": 3,
                "Cobalt": 2,
                "Silver": 1
            },
            "extras": {
                "Copper": 500,
                "Lead": 300,
                "Tin": 200,
                "Coal": 150,
                "Iron": 150,
                "Cobalt": 100,
                "Quartz": 50,
                "Silver": 25,
                "Gold": 5,
                "Sapphire": 5,
                "Ruby": 5,
                "Diamond": 0,
                "Emerald": 0,
                "Titanium": 0,
                "Meteorite": 0
            }
        },

        2: {
            "name": "Lead Pickaxe",
            "requirement": {
                "Copper": 12,
                "Lead": 30,
                "Coal": 20,
                "Iron": 10,
                "Silver": 3,
                "Quartz": 5
            },
            "extras": {
                "Copper": 1000,
                "Lead": 500,
                "Tin": 300,
                "Coal": 250,
                "Iron": 150,
                "Cobalt": 120,
                "Quartz": 150,
                "Silver": 50,
                "Gold": 10,
                "Sapphire": 10,
                "Ruby": 5,
                "Diamond": 2,
                "Emerald": 2,
                "Titanium": 0,
                "Meteorite": 0
            }
        },

        3: {
            "name": "Tin Pickaxe",
            "requirement": {
                "Copper" : 29,
                "Lead": 12,
                "Tin": 35,
                "Iron": 15,
                "Quartz": 10,
                "Gold": 2
            },
            "extras": {
                "Copper": 1200,
                "Lead": 800,
                "Tin": 500,
                "Coal": 300,
                "Iron": 250,
                "Cobalt": 200,
                "Quartz": 500,
                "Silver": 75,
                "Gold": 15,
                "Sapphire": 12,
                "Ruby": 12,
                "Diamond": 5,
                "Emerald": 3,
                "Titanium": 2,
                "Meteorite": 0
            }
        }
    }

    def __init__(self, bot):
        self.bot = bot
        self.mongodbm = MongoManager(MONGO_ADDRESS, DB_NAME)
        self.mongodbm.ConnectCollection("members")

    async def get_ore_inv(self, ctx, person: discord.User):
        # Get Member Data
        if person.bot is True:
            return
        user_data: dict = self.checkin_member(person.id)
        user_sack: dict = user_data["ores"]
        pick_level: int = user_data["pickaxe-level"]

        # Get Detail Sack of Ores
        ore_keys: list = list(self.kind_ores.keys())
        description_bag: str = "```"
        for i in range(len(ore_keys)):
            sentence: str
            ore_name: str = ore_keys[i]
            if i == len(ore_keys) - 1:
                sentence = "{:<12} : {} ({}%)".format(ore_name, user_sack[ore_name], self.kind_ores[ore_name] / 100)
            else:
                sentence = "{:<12} : {} ({}%)\n".format(ore_name, user_sack[ore_name], self.kind_ores[ore_name] / 100)
            description_bag += sentence
        description_bag += "```"
        
        # Print out Information
        emb = discord.Embed(title=f"💎 {person.display_name}'s Bag", description=description_bag, colour=discord.Colour(WHITE))
        emb.set_thumbnail(url="https://webstockreview.net/images/clipart-diamond-bunch-7.png")
        emb.set_footer(text=f"Pickaxe Level : {pick_level}")
        await ctx.send(embed=emb)

    def checkin_member(self, person_id: int) -> dict:
        """
        
        Check if Member is in the Database.

            Returns :
                (dict) => Member Information
        
        """
        query: dict = {"member_id":person_id}
        data: list = self.mongodbm.FindObject(query)
        if len(data) < 1:
            nd: dict = new_member_data
            nd["member_id"] = person_id
            self.mongodbm.InsertOneObject(nd)
            data = self.mongodbm.FindObject(query)
        return data[0]

    def rarity_randomize(self) -> str:
        """
        
        This is the Place Where you Mine Ores, Are you Lucky enough?

            Returns :
                (str) => Name of Ore you have Got
        
        """
        _list_of_gotem = []
        ore_keys: list = list(self.kind_ores.keys())
        for i in range(len(ore_keys)):
            ore_name: str = ore_keys[i]
            if self.approve(self.kind_ores[ore_name]) is True:
                _list_of_gotem.append(ore_name)
        if len(_list_of_gotem) == 0:
            return None
        else:
            return random.choice(_list_of_gotem)
        
    @staticmethod
    def approve(percentage: int) -> bool:
        """Randomize from 0 - 10000."""
        approved = random.randint(0, 10000)
        failed = 10000 - percentage
        if failed < approved:
            return True
        else:
            return False
        
    @commands.command(aliases=['mine'])
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def dig(self, ctx):
        # Digging Animation
        dig = "Dig... "
        emb = discord.Embed(title="⛏️ Mining...", description=dig, colour=discord.Colour(WHITE))
        queing: discord.Message = await ctx.send(embed=emb)
        await asyncio.sleep(0.5)
        for i in range(2):
            dig += "Dig... "
            emb = discord.Embed(title="⛏️ Mining...", description=dig, colour=discord.Colour(WHITE))
            await queing.edit(embed=emb)
            await asyncio.sleep(0.5)

        # Getting an Ore
        ore: str = self.rarity_randomize()
        failed = [
            "It's just a Rock... Throw it away!", 
            "Punching rock is hard, did you realize you forgot your pickaxe?", 
            "OMG Ghost! RUN!!!",
            "You went into the Lava, I told you not to dig straight down :v"
        ]

        # Print Out Result
        if ore is None:
            emb = discord.Embed(title="💨 Better Luck Next Time...", description=f"{random.choice(failed)}", colour=discord.Colour(WHITE))
            await queing.edit(embed=emb)
        else:
            person: discord.User = ctx.message.author
            emb = discord.Embed(
                title="💎 Bling!", 
                description=f"Yay {person.name}, You have got **{ore}**!", 
                colour=discord.Colour(WHITE)
            )
            await queing.edit(embed = emb)

            # Save Data
            user_bag: dict = self.checkin_member(person.id)["ores"]
            user_bag[ore] += 1
            query: dict = {"member_id":person.id}
            member_data: dict = self.mongodbm.FindObject(query)[0]
            member_data["ores"] = user_bag
            self.mongodbm.UpdateOneObject(query, member_data)  

    @commands.command()
    async def pickup(self, ctx):
        pass

    @dig.error
    async def mine_error(self, ctx, error):
        emb = discord.Embed(colour=discord.Colour(WHITE))
        if isinstance(error, commands.CommandOnCooldown):
            emb.add_field(name="💤 Zzzz... 💤", value="You have a fatigue, take a rest for **{0:.2f}** s.".format(error.retry_after))
            this_msg_coroute = await ctx.send(embed=emb)
            await asyncio.sleep(3)
            await this_msg_coroute.delete()

    @commands.command(aliases=['ore'])
    async def ores(self, ctx, person: discord.Member):
        await self.get_ore_inv(ctx, person)

    @ores.error
    async def ores_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await self.get_ore_inv(ctx, ctx.message.author)

def setup(bot):
    bot.add_cog(Mine(bot))