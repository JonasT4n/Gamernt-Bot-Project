import discord
import os
import datetime
import asyncio
from discord.ext import commands
from Settings.MyUtility import checkin_member, db_mbr

WHITE = 0xfffffe

class Profile(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Commands Area

    @commands.command(name="settitle", aliases=["st"])
    async def _settitle(self, ctx: commands.Context, *, ttl: str = None):
        if ttl is None:
            await ctx.send("Insert your profile title after the command")
        else:
            db_mbr.SetObject({"member_id": str(ctx.author.id)}, {"title": ttl})
            await ctx.send(f"*Title Set to {ttl}, Check your Profile.*")

    @commands.command(name="profile", aliases=["prof", "user"])
    async def _profile(self, ctx: commands.Context, *args):
        # Inner Function
        def get_age(start: datetime.datetime, end: datetime.datetime) -> str:
            days = (end - start).days
            years = days // 365
            months = (days - (years * 365)) // 30
            days = days - (years * 365) - (months * 30)
            return f"{years}Y {months}M {days}D"

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
        async with ctx.typing():
            user_title: str = checkin_member(person)["title"]
            roles: list = [role for role in ctx.guild.roles if role in ctx.author.roles]
            role_desc: str = " ".join([f"`{rm.name}`" for rm in roles])
            emb = discord.Embed(
                title=f"📜 Profile | {person.name}", 
                colour=WHITE
                )
            emb.add_field(
                name="Identity :",
                value=f"Title: __**{user_title}**__\n"
                    f"Nick: **{ctx.author.nick if ctx.author.nick is not None else person.name}**\n"
                    f"ID: `{person.id}`",
                inline=False
                )
            emb.add_field(
                name="Information :",
                value=f"Current Activity: `{ctx.author.activity}`\n"
                    f"Created At: `{person.created_at.strftime('%B %d %Y')}`\n"
                    f"Joined Server: `{person.joined_at.strftime('%B %d %Y')}`\n"
                    f"Account Age: `{get_age(person.created_at, datetime.datetime.now())}`\n"
                    f"Highest Role: `{person.top_role}`",
                inline=False
                )
            emb.add_field(
                name="Roles :",
                value=role_desc,
                inline=False
                )
            emb.set_thumbnail(url=person.avatar_url)
        await ctx.send(embed=emb)

    # Others

def setup(bot: commands.Bot):
    bot.add_cog(Profile(bot))