import discord
import random
from discord.ext import commands
from Settings.MyUtility import get_prefix

WHITE = 0xfffffe

class Chance(commands.Cog):

    pool_reply: list = [
        "Yes!",
        "No!",
        "Perhaps.",
        "Definitely.",
        "Of Course.",
        "Might.",
        "Maybe."
        ]

    ask_reply: list = [
        "I'm good, thank you :)",
        "Is that a Question?",
        "Anytime you wanted",
        "Shut Up! I'm busy",
        "Your Welcome mate :)",
        "Good times",
        "Nice PFP you have"
        ]

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

    @commands.command(name= "pool", pass_context= True)
    async def _pool(self, ctx: commands.Context, *, statement: str = ""):
        if len(statement) == 0:
            await ctx.send(embed = discord.Embed(
                title = "*Insert Your Statement after the Command*",
                description = f"Example : {get_prefix(ctx.guild.id)}pool Am I a good boy?"
                ))
        else:
            emb = discord.Embed(
                title=f"🎱 8 Pool", 
                description=f"{ctx.message.author.name} : {statement}\n\n__**{random.choice(self.pool_reply)}**__", 
                colour=discord.Colour(WHITE)
                )
            await ctx.send(embed = emb)

    @commands.command(name= "ask", pass_context= True)
    async def _ask(self, ctx: commands.Context, *, question: str):
        if len(question) == 0:
            await ctx.send(embed = discord.Embed(
                title = "*Insert Your Question after the Command*",
                description = f"Example : {get_prefix(ctx.guild.id)}ask How's your Day?"
                ))
        else:
            emb = discord.Embed(
                title=f"🦉 Ask Bot", 
                description=f"{ctx.message.author.name} : {question}\n\n__**{random.choice(self.ask_reply)}**__", 
                colour=discord.Colour(WHITE)
                )
            await ctx.send(embed = emb)

def setup(bot: commands.Bot):
    bot.add_cog(Chance(bot))