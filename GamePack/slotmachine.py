import discord
import random
from discord.ext import commands
from Settings.MongoManager import MongoManager
from Settings.MyUtility import checkin_member

WHITE = 0xfffffe

class SlotMachine(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.mongodbm = MongoManager(collection="members")

    # Listener Area

    @commands.Cog.listener()
    async def on_ready(self):
        print("Slot Machine is Ready!")

    # Command Area

    @commands.command(aliases=["slot"])
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def slot_machine(self, ctx: commands.Context, *args):
        bet: int
        if len(args) == 0:
            await self.slot_game(ctx.author, ctx.channel)

    # Others

    async def slot_game(self, person: discord.User, channel: discord.TextChannel):
        # Initialize Slot Machine
        list_of_element: list = ["7️⃣", "🚩", "💲", "💎"]
        screen_emb: discord.Embed = discord.Embed(
            title = "🎰 Slot Machine",
            description = "`X` `X` `X`",
            colour = discord.Colour(WHITE)
        )
        hm: discord.Message = await channel.send(embed = screen_emb)

        # Animate Embed
        loop: int = 5 # Loop Embed Animation
        desc: str
        for i in range(loop):
            desc = " ".join([random.choice(list_of_element) for j in range(3)])
            screen_emb: discord.Embed = discord.Embed(
                title = "🎰 Slot Machine",
                description = f"Rolling...\n\n`{desc}`",
                colour = discord.Colour(WHITE)
            )
            await hm.edit(embed = screen_emb)

        # Result
        result: list = [random.choice(list_of_element) for j in range(3)]
        desc = " ".join(result)
        screen_emb: discord.Embed = discord.Embed(
            title = "🎰 Slot Machine | Result",
            description = f"Result!!!\n\n`{desc}`",
            colour = discord.Colour(WHITE)
        )
        await hm.edit(embed = screen_emb)

def setup(bot: commands.Bot):
    bot.add_cog(SlotMachine(bot))

