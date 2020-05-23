import discord
import random
import threading
import asyncio
from discord.ext import commands
from Settings.MongoManager import MongoManager

WHITE = 0xfffffe

class OWS(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.mongodbm = MongoManager(collection="guilds")

    # Listener Area

    @commands.Cog.listener()
    async def on_ready(self):
        print("One Word Story Game is Ready!")

    # Checker Area

    def check_on_play(self, channel: discord.TextChannel):
        def inner_check(message: discord.Message):
            if not isinstance(message.channel, discord.DMChannel) and channel == message.channel and len(message.content.split(" ")) == 1:
                return True
            else:
                return False
        return inner_check

    # Command Area

    @commands.command(aliases=["OWS", "OWs", "Ows", "OwS", "oWS", "oWs", "owS"])
    async def ows(self, ctx: commands.Context, *args):
        if len(args) == 0:
            await self.print_help(ctx.channel)
        else: 
            # Play
            if args[0].lower() == "-p":
                await self.ows_on_play(ctx.channel)

            # Help
            elif args[0].lower() == "-h":
                await self.print_help(ctx.channel)

            # Read Story
            elif args[0].lower() == "-r":
                pass

            # Guild own Story
            elif args[0].lower() == "-os":
                pass

            # Delete Story
            elif args[0].lower() == "-del":
                pass
            
            # How to Play
            elif args[0].lower() == "-how":
                await self.manual(ctx.channel)
            
            # Else
            else:
                await self.print_help(ctx.channel)

    # Others

    def load_story(self, guild_id: int):
        pass

    @staticmethod
    async def manual(channel: discord.TextChannel):
        emb = discord.Embed(
            title="📚 One Word Story | Manual",
            description=open("./Help/ows_manual.txt").read(),
            colour=discord.Colour(WHITE)
        )
        await channel.send(embed=emb)

    @staticmethod
    async def ows_on_play(channel: discord.TextChannel):
        pass
    
    @staticmethod
    async def print_help(channel: discord.TextChannel):
        emb = discord.Embed(
            title="📚 One Word Story | Help",
            description=open("./Help/owsh.txt").read(),
            colour=discord.Colour(WHITE)
        )
        emb.set_footer(text="Example Command: g.ows -p")
        await channel.send(embed=emb)

def setup(bot):
    bot.add_cog(OWS(bot))