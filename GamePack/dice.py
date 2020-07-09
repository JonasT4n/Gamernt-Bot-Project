import discord
import random
import asyncio
from discord.ext import commands
from Settings.MyUtility import get_prefix

WHITE = 0xfffffe

class Dice(commands.Cog):

    def __init__(self, bot:commands.Bot):
        self.bot = bot

    # Command Area

    @commands.command(name="dice")
    async def _dice(self, ctx: commands.Context, amount: int = 2, dots: int = 6):
        if amount <= 0 or dots <= 0 or amount > 100 or dots > 100:
            await dice_help(ctx.channel)
        else:
            async with ctx.typing():
                ld: list = [random.randint(1, dots) for i in range(amount)]
                desc: str = "```"
                for i in ld:
                    desc += f"{i} "
                desc += "```"
                emb = discord.Embed(
                    title="🎲 Dice Rolled", 
                    description=f"{desc}\nSum of all Dice : **{sum(ld)}**", 
                    colour=WHITE
                    )
                emb.set_footer(text=f"{amount} Dices, {dots} Faces")
            await ctx.send(embed=emb)

    # Others

    @staticmethod
    async def dice_help(channel: discord.TextChannel):
        pref: str = get_prefix(channel.guild)
        emb = discord.Embed(
            title="🎲 Invalid Input", 
            description=f"> {pref}dice <amount> <dots>\n"
                "> Amount of Dice : 1 - 100\n"
                "> Dots on Dice : 1 - 100", 
            colour=WHITE
            )
        emb.set_footer(text=f"Ex : {pref}dice 10 10")
        await channel.send(embed=emb)
        
def setup(bot:commands.Bot):
    bot.add_cog(Dice(bot))