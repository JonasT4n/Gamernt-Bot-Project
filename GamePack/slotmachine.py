import discord
import random
import asyncio
from discord.ext import commands
from Settings.MongoManager import MongoManager
from Settings.MyUtility import checkin_member

WHITE = 0xfffffe

class SlotMachine(commands.Cog):

    list_of_element: list = ["7️⃣", "🚩", "💲", "💎"]

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.mongodbm = MongoManager(collection="members")

    # Event Listener Area

    @commands.Cog.listener()
    async def on_ready(self):
        print("Slot Machine is Ready!")

    # Checker Area

    @staticmethod
    def check_lottery(result: list or tuple) -> int:
        if result[0] == result[1] == result[2]:
            return 50
        elif result[0] == result[1] or result[0] == result[2] or result[1] == result[2]:
            return 20
        else:
            return 0

    # Command Area

    @commands.command(aliases=["slot"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def slot_machine(self, ctx: commands.Context, *args):
        bet: int
        if len(args) == 0:
            await self.slot_game(ctx.author, ctx.channel)

    # Command Error Handler

    @slot_machine.error
    async def mine_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandOnCooldown):
            emb = discord.Embed(
                title = "💤 Zzzz... 💤",
                description = "Calm Down, Take a rest for **{0:.2f}** s.".format(error.retry_after),
                colour = discord.Colour(WHITE)
            )
            this_msg_coroute = await ctx.send(embed=emb)
            await asyncio.sleep(3)
            await this_msg_coroute.delete()

    # Others

    async def slot_game(self, person: discord.User, channel: discord.TextChannel):
        # Initialize Slot Machine
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
            result: list = [random.choice(self.list_of_element) for j in range(3)]
            desc = " ".join(result)
            if i == loop - 1:
                earn_money: int = self.check_lottery(result)
                screen_emb: discord.Embed = discord.Embed(
                    title = "🎰 Slot Machine | Result",
                    description = f"Result!!!\n`{desc}`",
                    colour = discord.Colour(WHITE)
                )
                screen_emb.set_footer(text=f"You have Earned {earn_money} 💲")
                await hm.edit(embed = screen_emb)
                self.mongodbm.IncreaseItem({"member_id": str(person.id)}, {"money": earn_money})
            else:
                screen_emb: discord.Embed = discord.Embed(
                    title = "🎰 Slot Machine",
                    description = f"Rolling...\n`{desc}`",
                    colour = discord.Colour(WHITE)
                )
                await hm.edit(embed = screen_emb)

def setup(bot: commands.Bot):
    bot.add_cog(SlotMachine(bot))

