import discord
import random
import asyncio
import threading
from discord.ext import commands
from Settings.DbManager import DbManager as dbm

WHITE = 0xfffffe

# Paper Rock Scissor
class PRS(commands.Cog):

    rps_element = {1:"Paper ✋", 2:"Rock ✊", 3:"Scissor ✌"}
    block_option_embed = discord.Embed(title="Choose Wisely ✊✋✌", description="```1. Paper ✋\n2. Rock ✊\n3. Scissor ✌\n\nSend your Option Here in DM (1-3).\nExample : 1```", colour=discord.Colour(WHITE))

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = dbm.connect_db("./DataPack/guild.db")

    async def begin(self, p1 : discord.User, p2 : discord.User, channel : discord.TextChannel):
        try:
            # Initiate Hint Message in Channel
            handle_msg: discord.Message = await channel.send(content=f"**Waiting for {p1.name} to choose.**")

            # Player 1 Answer
            fpmsg: discord.Message = await p1.send(embed = self.block_option_embed)
            reply_p1 = await self.bot.wait_for(event='message', check=self.check_choosen(p1), timeout=30)
            await fpmsg.delete()

            # Edit handler on Channel
            await handle_msg.edit(content=f"**Waiting for {p2.name} to choose.**")

            # Player 2 Answer
            spmsg: discord.Message = await p2.send(embed = self.block_option_embed)
            reply_p2 = await self.bot.wait_for(event='message', check=self.check_choosen(p2), timeout=30)
            await spmsg.delete()

            # 1. Paper ✋ 2. Rock ✊ 3. Scissor ✌
            winner = self.check_rps_winner(p1, p2, reply_p1.content, reply_p2.content)
            descript = f"```{p1.name} : {self.rps_element[int(reply_p1.content)]}\n{p2.name} : {self.rps_element[int(reply_p2.content)]}\n{winner}!```"
            emb = discord.Embed(title="✊✋✌ Rock Paper Scissor", description=descript, colour=discord.Colour(WHITE))
            await handle_msg.delete()
            await channel.send(embed = emb)

        except asyncio.TimeoutError:
            await channel.send(f"*Timeout, The Game has stopped. :v*")

    async def against_bot(self, person: discord.User, channel: discord.TextChannel):
        await channel.send(embed = self.block)

    def check_rps_winner(self, p1:discord.User, p2:discord.User, p1_reply:str, p2_reply:str):
        if p1_reply == p2_reply:
            return "It's a DRAW"
        elif (p1_reply == '1' and p2_reply == '2') or (p1_reply == '2' and p2_reply == '3') or (p1_reply == '3' and p2_reply == '1'):
            return f"Winner is {p1.name}!"
        else:
            return f"Winner is {p2.name}!"

    def check_choosen(self, person):
        def inner_check(message):
            if (int(message.content) > 0 or int(message.content) < 4) and person == message.author and isinstance(message.channel, discord.DMChannel):
                return True
            else:
                return False
        return inner_check

    def check_challanger_reply(self, person, channel):
        def inner_check(message):
            if message.channel == channel and message.author.id == person.id and (message.content.lower() == 'y' or message.content.lower() == 'n'):
                return True
            else:
                return False
        return inner_check

    @commands.command(aliases=['Rps', 'rPs', 'rpS', 'RPs', 'RpS', 'rPS', 'RPS'])
    async def rps(self, ctx, *, against: discord.Member = None):
        emb = discord.Embed(title="✊✋✌ Rock Paper Scissor", description=f"**{ctx.message.author.name}** wants to challange you, will you Accept?", colour=discord.Colour(WHITE))
        emb.set_footer(text="Type 'Y' to accept or 'N' to abort.")
        handler = await ctx.send(embed=emb)
        if against is not None:
            if not against.bot:
                try:
                    reply = await self.bot.wait_for(event='message', check=self.check_challanger_reply(against, ctx.message.channel), timeout=30)
                    await handler.delete()
                    if reply.content.lower() == 'n':
                        await reply.delete()
                        await ctx.send("*Challenge Not Accepted :v*")
                    else:
                        await reply.delete()
                        threading.Thread(target = await self.begin(ctx.message.author, against, ctx.message.channel)).start()
                except asyncio.TimeoutError:
                    await handler.delete()
                    await ctx.send("*Request Timeout.*")
            else:
                await ctx.send("You can't Challange Bot :v")
        else:
            threading.Thread(target= await self.against_bot(ctx.message.author, ctx.message.channel))

def setup(bot: commands.Bot):
    bot.add_cog(PRS(bot))