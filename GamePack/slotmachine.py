import discord
import random
import asyncio
from discord.ext import commands

WHITE = 0xfffffe

class SlotMachine(commands.Cog):

    list_of_element: list = ["7️⃣", "🚩", "💲", "💎"]

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Command Area

    @commands.command(aliases=["slot"])
    async def slot_machine(self, ctx: commands.Context):
        await self.slot_game(ctx.author, ctx.channel)

    # Others

    async def slot_game(self, person: discord.User, channel: discord.TextChannel):
        # Initialize Slot Machine
        screen_emb: discord.Embed = discord.Embed(
            title="🎰 Slot Machine",
            description="> `X` `X` `X`",
            colour=WHITE
            )
        hm: discord.Message = await channel.send(embed=screen_emb)

        # Animate Embed
        loop: int = 5 # Loop Embed Animation
        desc: str
        for i in range(loop):
            result: list = [random.choice(self.list_of_element) for j in range(3)]
            desc = " ".join(result)
            if i == loop - 1:
                screen_emb: discord.Embed = discord.Embed(
                    title="🎰 Slot Machine | Result!",
                    description="> " + desc,
                    colour=WHITE
                    )
                screen_emb.set_author(
                    name=f"{person.name}",
                    icon_url=person.avatar_url
                    )
                if result[0] == result[1] == result[2]:
                    screen_emb.set_footer(text="JACKPOT!!!")
                await hm.edit(embed=screen_emb)
            else:
                screen_emb: discord.Embed = discord.Embed(
                    title="🎰 Slot Machine | Rolling...",
                    description="> " + desc,
                    colour=WHITE
                    )
                await hm.edit(embed=screen_emb)

def setup(bot: commands.Bot):
    bot.add_cog(SlotMachine(bot))

