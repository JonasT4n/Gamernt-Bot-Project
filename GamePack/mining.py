import discord
import asyncio
import random
from discord.ext import commands
from Settings.MongoManager import MongoManager, new_member_data
from Settings.setting import MONGO_ADDRESS, DB_NAME

WHITE = 0xfffffe

class Mine(commands.Cog):

    # Pickaxe Identity
    pickaxe_identity: dict = {
        0: {
            "name": "Stone Pickaxe",
            "requirement": None,
            "balance": {
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
            "balance": {
                "Copper": 3000,
                "Lead": 1500,
                "Tin": 1000,
                "Coal": 650,
                "Iron": 450,
                "Cobalt": 350,
                "Quartz": 250,
                "Silver": 145,
                "Gold": 105,
                "Sapphire": 90,
                "Ruby": 80,
                "Diamond": 30,
                "Emerald": 20,
                "Titanium": 10,
                "Meteorite": 6
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
            "balance": {
                "Copper": 3500,
                "Lead": 1750,
                "Tin": 1500,
                "Coal": 800,
                "Iron": 500,
                "Cobalt": 350,
                "Quartz": 300,
                "Silver": 175,
                "Gold": 125,
                "Sapphire": 100,
                "Ruby": 90,
                "Diamond": 35,
                "Emerald": 30,
                "Titanium": 18,
                "Meteorite": 8
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
            "balance": {
                "Copper": 3750,
                "Lead": 2200,
                "Tin": 1800,
                "Coal": 1000,
                "Iron": 800,
                "Cobalt": 500,
                "Quartz": 450,
                "Silver": 305,
                "Gold": 245,
                "Sapphire": 120,
                "Ruby": 120,
                "Diamond": 50,
                "Emerald": 35,
                "Titanium": 25,
                "Meteorite": 10
            }
        }
    }

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.mongodbm = MongoManager(MONGO_ADDRESS, DB_NAME)
        self.mongodbm.ConnectCollection("members")

    @commands.Cog.listener()
    async def on_ready(self):
        print("Miner is Ready!")

    def check_confirm(self, person: discord.User):
        def inner_check(message: discord.Message):
            if message.author == person:
                return True
            else:
                return False
        return inner_check

    async def get_ore_inv(self, ctx, person: discord.User):
        # Get Member Data
        if person.bot is True:
            return
        user_data: dict = self.checkin_member(person.id)
        user_sack: dict = user_data["ores"]
        pick_level: int = user_data["pickaxe-level"]

        # Get Detail Sack of Ores
        ore_keys: list = list(self.pickaxe_identity[pick_level]["balance"].keys())
        description_bag: str = "```"
        for i in range(len(ore_keys)):
            sentence: str
            ore_name: str = ore_keys[i]
            if i == len(ore_keys) - 1:
                sentence = "{:<12} : {} ({}%)".format(ore_name, user_sack[ore_name], self.pickaxe_identity[pick_level]["balance"][ore_name] / 100)
            else:
                sentence = "{:<12} : {} ({}%)\n".format(ore_name, user_sack[ore_name], self.pickaxe_identity[pick_level]["balance"][ore_name] / 100)
            description_bag += sentence
        description_bag += "```"
        
        # Print out Information
        emb = discord.Embed(title=f"💎 {person.display_name}'s Bag", description=description_bag, colour=discord.Colour(WHITE))
        emb.set_thumbnail(url="https://webstockreview.net/images/clipart-diamond-bunch-7.png")
        emb.set_footer(text=f"Pickaxe Level : {pick_level} | {self.pickaxe_identity[pick_level]['name']}")
        await ctx.send(embed=emb)

    def checkin_member(self, person_id: int) -> dict:
        """
        
        Check if Member is in the Database.

            Returns :
                (dict) => Member Information
        
        """
        query: dict = {"member_id":str(person_id)}
        u_data = self.mongodbm.FindObject(query)
        if u_data is None:
            nd: dict = new_member_data
            nd["member_id"] = str(person_id)
            self.mongodbm.InsertOneObject(nd)
            return nd
        else:
            return u_data[0]

    def rarity_randomize(self, pickaxe_level: int) -> str:
        """
        
        This is the Place Where you Mine Ores, Are you Lucky enough?

            Returns :
                (str) => Name of Ore you have Got
        
        """
        _list_of_gotem = []
        ore_keys: list = list(self.pickaxe_identity[pickaxe_level]["balance"].keys())
        for i in range(len(ore_keys)):
            ore_name: str = ore_keys[i]
            if self.approve(self.pickaxe_identity[pickaxe_level]["balance"][ore_name]) is True:
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
        person: discord.User = ctx.message.author
        user_bag: dict = self.checkin_member(person.id)
        ore: str = self.rarity_randomize(user_bag["pickaxe-level"])
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
            emb = discord.Embed(
                title="💎 Bling!", 
                description=f"Yay {person.name}, You have got **{ore}**!", 
                colour=discord.Colour(WHITE)
            )
            await queing.edit(embed = emb)

            # Save Data
            query: dict = {"member_id":str(person.id)}
            user_bag["ores"][ore] += 1
            del user_bag["_id"]
            self.mongodbm.UpdateOneObject(query, user_bag)  

    @commands.command()
    async def pickaxeup(self, ctx):
        # Initialize Things
        able_upgrade: bool = True
        person: discord.User = ctx.message.author
        user_data: dict = self.checkin_member(person.id)
        del user_data["_id"]
        sack_of_ores: dict = user_data["ores"]
        pick_level: int = user_data["pickaxe-level"]
        next_level_name: str = self.pickaxe_identity[pick_level + 1]["name"]
        requirement: dict = self.pickaxe_identity[pick_level + 1]["requirement"]
        list_required: list = list(requirement.keys())

        # Check if it is Able to Upgrade
        req_text: str = "```"
        for i in range(len(list_required)):
            if sack_of_ores[list_required[i]] < requirement[list_required[i]]:
                able_upgrade = False
            if i == len(list_required) - 1:
                req_text += "{:<12} : {}/{}".format(list_required[i], sack_of_ores[list_required[i]], requirement[list_required[i]])
            else:
                req_text += "{:<12} : {}/{}\n".format(list_required[i], sack_of_ores[list_required[i]], requirement[list_required[i]])
        req_text += "```"

        # Print Out Requirements and Confirmation
        emb = discord.Embed(
            title=f"⛏️ Upgrade Pickaxe to {next_level_name}?", 
            description=f"**Requirements** : \n{req_text}",
            colour = discord.Colour(WHITE)
        )
        if not able_upgrade:
            emb.set_footer(text="Sorry, Not Enough Materials.")
            await ctx.send(embed = emb)
        else:
            emb.set_footer(text = "Will you Upgrade it? type 'Upgrade' to Upgrade.")
            handler_msg: discord.Message = await ctx.send(embed = emb)
            try:
                replied: discord.Message = await self.bot.wait_for(event="message", check=self.check_confirm(ctx.message.author), timeout=30.0)
                if replied.content.lower() == "upgrade":
                    await handler_msg.delete()
                    emb = discord.Embed(
                        title=f"🎉 Pickaxe has been Upgraded to {next_level_name}?", 
                        description=f"⛏️ See the Stat in g.ores",
                        colour = discord.Colour(WHITE)
                    )
                    await ctx.send(embed = emb)
                else:
                    emb.set_footer(text="Ok, Next Time!")
                    await handler_msg.edit(embed = emb)
            except asyncio.TimeoutError:
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