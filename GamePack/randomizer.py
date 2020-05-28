import discord
import random
from discord.ext import commands

WHITE = 0xfffffe

class Chance(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Event Listener Area

    @commands.Cog.listener()
    async def on_ready(self):
        print("Randomizer Machine is Ready!")

    # Commands Area

    @commands.command()
    async def chance(self, ctx, *, statement: str):
        emb = discord.Embed(
            title=f"⭐ Chance of Everything", 
            description=f"\"{statement}\"\nThe Chance is **{random.randint(0, 100)}%**", 
            colour=discord.Colour(WHITE)
        )
        await ctx.send(embed=emb)

    @commands.command()
    async def pool(self, ctx: commands.Context, *, statement: str = ""):
        if len(statement) == 0:
            await ctx.send("*Insert Your Statement or Question after the Command*")
            return

        reply = [
            "Yes!",
            "No!",
            "Perhaps.",
            "Definitely.",
            "Of Course.",
            "Might.",
            "Maybe."
        ]
        emb = discord.Embed(
            title=f"🦉 You ask for it.", 
            description=f"{ctx.message.author.name} : {statement}\n\n__**{random.choice(reply)}**__", 
            colour=discord.Colour(WHITE)
        )
        await ctx.send(embed = emb)

    # Others

def setup(bot: commands.Bot):
    bot.add_cog(Chance(bot))