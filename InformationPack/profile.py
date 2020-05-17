import discord
import os
import asyncio
from discord.ext import commands
from Settings.MongoManager import MongoManager, new_member_data
from Settings.setting import MONGO_ADDRESS, DB_NAME

WHITE = 0xfffffe

class Profile(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.mongodbm = MongoManager(MONGO_ADDRESS, DB_NAME)
        self.mongodbm.ConnectCollection("members")

    @commands.command(aliases=["prof", "user"])
    async def profile(self, ctx, *args):
        # Get Player ID
        person: discord.User
        person_id: int
        if len(args) == 0:
            person = ctx.message.author
            person_id = person.id
        elif "@!" in args[0]:
            person_id = int(args[0].split('!')[1].split('>')[0])
            person: discord.User = await self.bot.fetch_user(person_id)

        # Check if it is a Bot, not Member
        if person.bot is True:
            return
        
        # Make Query
        user: dict
        query: dict = {"member_id": person_id}
        data_user = self.mongodbm.FindObject(query)
        if data_user is None:
            nd = new_member_data
            nd["member_id"] = person_id
            self.mongodbm.InsertOneObject(nd)
            user = nd
        else:
            user = data_user[0]
        
        # Print Out Profile Information
        emb = discord.Embed(
            title=f"{ctx.message.author.name}'s Profile", 
            description=f"""```ID : {person_id}\n🏆 : {user["trophy"]}\n👛 : {user["money"]}```""", 
            colour=discord.Colour(WHITE)
        )
        emb.set_thumbnail(url=person.avatar_url)
        emb.set_footer(text="This is your Current Profile in this Application")
        await ctx.send(embed = emb)

def setup(bot: commands.Bot):
    bot.add_cog(Profile(bot))