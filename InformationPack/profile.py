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
        self.mongodbm = MongoManager(collection = "members")

    # Event Listener Area

    @commands.Cog.listener()
    async def on_ready(self):
        print("Virtual Profile is Ready!")

    # Commands Area

    @commands.command(name= "leaderboard", aliases= ["lb"], pass_context = True)
    async def _lb(self, ctx):
        pass

    @commands.command(name= "settitle", aliases= ["st"])
    async def _settitle(self, ctx: commands.Context, *, ttl: str = None):
        if ttl is None:
            await ctx.send("Insert your profile title after the command")
        else:
            self.mongodbm.SetObject({"member_id": str(ctx.author.id)}, {"title": ttl})
            await ctx.send(f"*Title Set to {ttl}, Check your Profile.*")

    @commands.command(name= "profile", aliases= ["prof", "user"], pass_context = True)
    async def _profile(self, ctx: commands.Context, *args):
        # Get Player ID
        person: discord.User
        if len(args) == 0:
            person = ctx.message.author
        elif "@!" in args[0]:
            person_id = int(args[0].split('!')[1].split('>')[0])
            person = await self.bot.fetch_user(person_id)

        # Check if it is a Bot, not Member
        if person.bot is True:
            return

        # Print Out Profile Information
        user_title: str = checkin_member(person.id)["title"]
        roles: list = [role for role in ctx.guild.roles if role in ctx.author.roles]
        role_desc: str = " ".join([f"`{rm.name}`" for rm in roles])
        emb = discord.Embed(
            title = f"📜 Profile | {ctx.author.nick if ctx.author.nick is not None else person.name}", 
            description = f"""> Title: __**{user_title}**__
                        > Name: **{person.display_name}**
                        > ID: `{person.id}`
                        > Current Activity: `{ctx.author.activity}`\n
                        > Created At: `{person.created_at.strftime("%B %d %Y")}`
                        > Joined Server: `{person.joined_at.strftime("%B %d %Y")}`
                        > Highest Role: `{person.top_role}`\n
                        > Roles: \n{role_desc}""",
            colour = discord.Colour(WHITE)
        )
        emb.set_thumbnail(url=person.avatar_url)
        await ctx.send(embed = emb)

    # Others

def setup(bot: commands.Bot):
    bot.add_cog(Profile(bot))