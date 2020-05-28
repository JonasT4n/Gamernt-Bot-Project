import discord
import os
import asyncio
from discord.ext import commands
from Settings.MyUtility import checkin_member
from Settings.MongoManager import MongoManager

WHITE = 0xfffffe

class Profile(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.mongodbm = MongoManager(collection="members")

    # Event Listener Area

    @commands.Cog.listener()
    async def on_ready(self):
        print("Virtual Profile is Ready!")

    # Commands Area

    @commands.command(aliases=["lb"])
    async def leaderboard(self, ctx):
        pass

    @commands.command(aliases=["st"])
    async def settitle(self, ctx: commands.Context, *args):
        person_data: dict = checkin_member(ctx.author.id)
        title: str = " ".join(args)
        person_data["title"] = title
        if "_id" in person_data:
            del person_data["_id"]
        self.mongodbm.SetObject({"member_id": str(ctx.author.id)}, person_data)
        await ctx.send(f"*Title Set to {title}, Check your Profile.*")

    @commands.command(aliases=["prof", "user"], pass_context = True)
    async def profile(self, ctx: commands.Context, *args):
        # Get Player ID
        person: discord.User
        person_id: int
        if len(args) == 0:
            person = ctx.message.author
            person_id = person.id
        elif "@!" in args[0]:
            person_id = int(args[0].split('!')[1].split('>')[0])
            person = await self.bot.fetch_user(person_id)

        # Check if it is a Bot, not Member
        if person.bot is True:
            return

        # Print Out Profile Information
        user: dict = checkin_member(person.id)
        emb = discord.Embed(
            title=f"{ctx.message.author.name}", 
            description=f"""The **{user["title"]}**\n📜 ID : `{person_id}`\n🏆 Trophy : `{user["trophy"]}`\n👛 Money : `{user["money"]}`\n\nCreated At : `{person.created_at.strftime("%B %d %Y")}`\n Joined `{ctx.guild.name}` at : `{person.joined_at.strftime("%B %d %Y")}`""", 
            colour=discord.Colour(WHITE)
        )
        roles: list = [role for role in ctx.guild.roles if role in ctx.author.roles]
        emb.add_field(
            name = "Roles",
            value = " ".join([f"`{rm.name}`" for rm in roles]),
            inline = False
        )
        emb.set_thumbnail(url=person.avatar_url)
        emb.set_footer(text="This is your Current Profile in this Application")
        await ctx.send(embed = emb)

    # Others

def setup(bot: commands.Bot):
    bot.add_cog(Profile(bot))