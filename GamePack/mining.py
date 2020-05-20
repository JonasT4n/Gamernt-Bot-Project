import discord
import asyncio
import random
from discord.ext import commands
from Settings.MongoManager import MongoManager, new_member_data
from Settings.setting import MONGO_ADDRESS, DB_NAME
from Settings.StaticData import pickaxe_identity

WHITE = 0xfffffe

class Mine(commands.Cog):

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
        pickaxe_name: str = user_data["pickaxe-name"]

        # Get Detail Sack of Ores
        ore_keys: list = list(pickaxe_identity[pick_level]["balance"].keys())
        description_bag: str = "```"
        for i in range(len(ore_keys)):
            sentence: str
            ore_name: str = ore_keys[i]
            if i == len(ore_keys) - 1:
                sentence = "{:.<12}{} ({}%)".format(ore_name, user_sack[ore_name], pickaxe_identity[pick_level]["balance"][ore_name] / 100)
            else:
                sentence = "{:.<12}{} ({}%)\n".format(ore_name, user_sack[ore_name], pickaxe_identity[pick_level]["balance"][ore_name] / 100)
            description_bag += sentence
        description_bag += "```"
        
        # Print out Information
        emb = discord.Embed(title=f"💎 {person.display_name}'s' Sack Of Ores", description=f"{pickaxe_name}\nPickaxe Level : {pick_level}\n{description_bag}", colour=discord.Colour(WHITE))
        emb.set_thumbnail(url="https://webstockreview.net/images/coal-clipart-bag-coal-6.png")
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
        ore_keys: list = list(pickaxe_identity[pickaxe_level]["balance"].keys())
        for i in range(len(ore_keys)):
            ore_name: str = ore_keys[i]
            if self.approve(pickaxe_identity[pickaxe_level]["balance"][ore_name]) is True:
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
        pickaxe_name: str = user_data["pickaxe-name"]
        requirement: dict = pickaxe_identity[pick_level + 1]["requirement"]
        list_required: list = list(requirement.keys())

        # Check if it is Able to Upgrade
        req_text: str = "```"
        for i in range(len(list_required)):
            if sack_of_ores[list_required[i]] < requirement[list_required[i]]:
                able_upgrade = False
            if i == len(list_required) - 1:
                req_text += "{:.<12}{}/{}".format(list_required[i], sack_of_ores[list_required[i]], requirement[list_required[i]])
            else:
                req_text += "{:.<12}{}/{}\n".format(list_required[i], sack_of_ores[list_required[i]], requirement[list_required[i]])
        req_text += "```"

        # Print Out Requirements and Confirmation
        emb = discord.Embed(
            title=f"⛏️ Want to Upgrade your {pickaxe_name}?", 
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
                        title=f"🎉 {pickaxe_name} has been Upgraded", 
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