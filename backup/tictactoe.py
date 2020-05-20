import discord
import asyncio
import threading
from discord.ext import commands
from Settings.MongoManager import MongoManager, new_member_data

WHITE = 0xfffffe

class Tictactoe(commands.Cog):

    template: dict = {
        "3x3":
        """
        1|2|3\n
        4|5|6\n
        7|8|9
        """,
        "4x4":
        """
        1|2|3|4\n
        5|6|7|8\n
        9|10|11|12\n
        13|14|15|16
        """
    }

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def check_challanger_reply(self, person, channel):
        def inner_check(message):
            if message.channel == channel and message.author.id == person.id and (message.content.lower() == 'y' or message.content.lower() == 'n'):
                return True
            else:
                return False
        return inner_check

    async def begin(self, channel, p1, p2):
        pass

    @commands.command(aliases=['ttt'])
    async def tictactoe(self, ctx, *, person: discord.Member):
        emb = discord.Embed(title="❌🟢 Tic Tac Toe", description=f"**{ctx.message.author.name}** wants to challange you, will you Accept?", colour=discord.Colour(WHITE))
        emb.set_footer(text="Type 'Y' to accept or 'N' to abort.")
        handler_msg = await ctx.send(embed=emb)

        if not person.bot:
            try:
                reply = self.bot.wait_for(event="message", check=self.check_challanger_reply(person, ctx.message.channel), timeout=30)
                await handler_msg.delete()
                if reply.content.lower() == 'y':
                    threading.Thread(target=await self.begin(ctx.message.channel, ctx.message.author, person))
                else:
                    await ctx.send("*Challenge Not Accepted :v*")
            except asyncio.TimeoutError:
                await handler_msg.delete()
                await ctx.send("*Request Timeout.*")
        else:
            await ctx.send("You can't Challange Bot :v")
        



def setup(bot : commands.Bot):
    bot.add_cog(Tictactoe(bot))