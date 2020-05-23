import discord
import random
import asyncio
import threading
from discord.ext import commands
from Settings.MyUtility import checkin_member
from Settings.MongoManager import MongoManager, new_member_data

WHITE = 0xfffffe

# Paper Rock Scissor
class RPS(commands.Cog):

    rps_element = {1:"Paper ✋", 2:"Rock ✊", 3:"Scissor ✌"}
    block_option_embed = discord.Embed(title="Choose Wisely ✊✋✌", description="```1. Paper ✋\n2. Rock ✊\n3. Scissor ✌\n\nSend your Option Here (1-3).\nExample : 1```", colour=discord.Colour(WHITE))

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.mongodbm = MongoManager(collection="members")
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("Rock Paper Scissor is Ready!")

    def check_choosen(self, person):
        def inner_check(message: discord.Message):
            if (int(message.content) > 0 or int(message.content) < 4) and person == message.author and isinstance(message.channel, discord.DMChannel):
                return True
            else:
                return False
        return inner_check

    def check_choosen_against_bot(self, person, channel):
        def inner_check(message: discord.Message):
            if (int(message.content) > 0 or int(message.content) < 4) and person == message.author and message.channel == channel:
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

    async def against_bot(self, person: discord.User, channel: discord.TextChannel):
        msg: discord.Message = await channel.send(embed = self.block_option_embed)
        try:
            # Waiting for User Answer
            replied = await self.bot.wait_for(event='message', check=self.check_choosen_against_bot(person, channel), timeout=30)
            await msg.delete()
            await replied.delete()

            # Checking if User Win or Bot Win
            winner: str = ""
            earned: int = 5
            bot_choose: str = str(random.choice(list(self.rps_element)))

            if replied.content == bot_choose:
                winner = "It's a DRAW"
            elif (replied.content == '1' and bot_choose == '2') or (replied.content == '2' and bot_choose == '3') or (replied.content == '3' and bot_choose == '1'):
                winner = f"You Win! Earned {earned} 💲"
                user_data: dict = checkin_member(person.id)
                del user_data["_id"]
                user_data["money"] += earned
                self.mongodbm.UpdateOneObject({"member_id": str(person.id)}, user_data)
            else:
                winner = f"Better Luck Next Time."

            # Announce the Winner
            descript = f"```{person.name} : {self.rps_element[int(replied.content)]}\nMe : {self.rps_element[int(bot_choose)]}\n{winner}!```"
            emb = discord.Embed(title="✊✋✌ Rock Paper Scissor", description=descript, colour=discord.Colour(WHITE))
            await channel.send(embed = emb)

        except asyncio.TimeoutError:
            await msg.delete()
            await channel.send(content="*Game Timeout :v*")

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

            # Check either Player 1 or Player 2 Win
            winner: str = ""
            earned: int = random.randint(1, 2)
            if reply_p1.content == reply_p2.content:
                winner = "It's a DRAW"
            elif (reply_p1.content == '1' and reply_p2.content == '2') or (reply_p1.content == '2' and reply_p2.content == '3') or (reply_p1.content == '3' and reply_p2.content == '1'):
                winner = f"Winner is {p1.name}!"
                user_data: dict = checkin_member(p1.id)
                user_data["money"] += earned
                self.mongodbm.UpdateOneObject({"member_id": str(p1.id)}, user_data)
            else:
                winner = f"Winner is {p2.name}!"
                user_data: dict = checkin_member(p2.id)
                user_data["money"] += earned
                self.mongodbm.UpdateOneObject({"member_id": str(p2.id)}, user_data)
            
            # Announce the Winner
            descript = f"```{p1.name} : {self.rps_element[int(reply_p1.content)]}\n{p2.name} : {self.rps_element[int(reply_p2.content)]}\n{winner}!```"
            emb = discord.Embed(title="✊✋✌ Rock Paper Scissor", description=descript, colour=discord.Colour(WHITE))
            await handle_msg.delete()
            await channel.send(embed = emb)

        except asyncio.TimeoutError:
            await channel.send(f"*Timeout, The Game has stopped. :v*")

    @commands.command(aliases=['Rps', 'rPs', 'rpS', 'RPs', 'RpS', 'rPS', 'RPS'])
    async def rps(self, ctx, *, against: discord.Member = None):
        if against is None:
            threading.Thread(target= await self.against_bot(ctx.message.author, ctx.message.channel))
        else:
            emb = discord.Embed(title="✊✋✌ Rock Paper Scissor", description=f"**{ctx.message.author.name}** wants to challange you, will you Accept?", colour=discord.Colour(WHITE))
            emb.set_footer(text="Type 'Y' to accept or 'N' to abort.")
            handler = await ctx.send(embed=emb)
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
            

def setup(bot: commands.Bot):
    bot.add_cog(RPS(bot))