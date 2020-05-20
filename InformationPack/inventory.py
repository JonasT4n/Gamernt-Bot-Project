import discord
import asyncio
from discord.ext import commands
from Settings.MongoManager import MongoManager, new_member_data
from Settings.setting import MONGO_ADDRESS, DB_NAME
from Settings.StaticData import pickaxe_identity

WHITE = 0xfffffe

class Inventory(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.mongodbm = MongoManager(MONGO_ADDRESS, DB_NAME)
        self.mongodbm.ConnectCollection("members")

    def user_check(self, person: discord.User):
        def inner_check(message: discord.Message):
            if person == message.author:
                return True
            else:
                return False
        return inner_check

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

    async def ore_inventory(self, message: discord.Message, person: discord.User):
        """Only for Inventory."""
        # Get Member Data
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

        # Edit Menu with This Data Detail
        emb = discord.Embed(title=f"💎 {person.display_name}'s' Sack Of Ores", description=f"{pickaxe_name}\nPickaxe Level : {pick_level}\n{description_bag}", colour=discord.Colour(WHITE))
        emb.set_thumbnail(url="https://webstockreview.net/images/coal-clipart-bag-coal-6.png")
        await message.edit(embed=emb)

    async def main_menu(self, message: discord.Message):
        pass

    @commands.command(aliases=["inv"])
    async def inventory(self, ctx: commands.Context):
        tud: dict = self.checkin_member(ctx.author.id)
        menu_emb = discord.Embed(
            title=f"{ctx.author.display_name}'s Inventory",
            description=f"👛 Money : {tud['money']}\n1. Ores",
            colour=discord.Colour(WHITE)
        )
        menu_emb.set_footer(text="Check Detail by Number")
        handler_message: discord.Message = await ctx.send(embed = menu_emb)
        try:
            answered: discord.Message = await self.bot.wait_for(event="message", check=self.user_check(ctx.author), timeout=30.0)
            if answered.content == "1":
                await answered
                await self.ore_inventory(handler_message, ctx.author)
        except asyncio.TimeoutError:
            pass

def setup(bot: commands.Bot):
    bot.add_cog(Inventory(bot))