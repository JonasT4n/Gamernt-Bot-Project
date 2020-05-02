import discord
import asyncio
import random
import datetime
import threading
from discord.ext import commands

WHITE = 0xfffffe

class Choose(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Choosing System is Ready!")

    def check_giveaway_duration(self, author):
        def inner_check(message):
            if message.author == author:
                list_char = message.content.split(' ')
                if len(list_char) == 2:
                    for elemen in list_char:
                        if len(elemen) > 2:
                            return False
                        else:
                            for word in elemen:
                                if ord(word) < 48 and ord(word) >= 58:
                                    return False
                    return True
                else:
                    return False
            else:
                return False
        return inner_check

    def convert_time_for_giveaway(self, content):
        result, spl = 0, content.split()
        for elemen in range(len(spl)):
            if elemen == 0:
                result += int(spl[elemen]) * 60
            elif elemen == 1:
                result += int(spl[elemen])
        return result

    def check_giveaway_many_people(self, author):
        def inner_check(message):
            if message.author == author:
                for word in message.content:
                    if ord(word) < 48 and ord(word) >= 58:
                        return False
                return True
            else:
                return False
        return inner_check

    async def co_gw(self, dur, ctx, desc, ppl: int):
        emb = discord.Embed(title="⌛ Waiting for Contributor! ⌛", colour=discord.Colour(WHITE))
        emb.add_field(name="By {}".format(ctx.message.author.name), value="{}".format(desc), inline=False)
        emb.set_footer(text="Started on {} at {}; React this TADA to Join".format(datetime.datetime.now().date(), datetime.datetime.now().strftime("%H:%M:%S")))
        wait_msg = await ctx.send(embed=emb)
        await wait_msg.add_reaction(u"\U0001F389")

        # Waiting for certain Time (This is not Effective)
        await asyncio.sleep(dur)

        # Update Giveaway
        get_updated_msg = discord.utils.get(self.bot.cached_messages, id=wait_msg.id)
        all_ppl_joined = await get_updated_msg.reactions[0].users().flatten()
        del all_ppl_joined[0]
        winner: list = []
        if len(all_ppl_joined) < ppl:
            winner = [i.mention for i in all_ppl_joined]
        else:
            while ppl > 0:
                new_winner = random.choice(all_ppl_joined)
                if new_winner not in winner and new_winner.bot is False:
                    winner.append(new_winner.mention)
                    ppl -= 1
                else:
                    continue
        desc_win: str = "\n".join(winner) + f"\n\n Winning for : **{desc}**"
        emb = discord.Embed(colour=discord.Colour(WHITE))
        emb.add_field(name="🎉 Congratulation! The winner is :", value=desc_win, inline=False)
        emb.add_field(name="Award :", value="{}".format(desc), inline=False)
        await ctx.send(embed=emb)

    async def help_giveaway(self, ctx):
        emb = discord.Embed(title="🎁 Giveaway - Help", description="```Yay, it's a Giveaway!!!\n1. Insert the Description\n2. Insert How much Time until Announcement\n3. Insert how many people will win it.```", colour=discord.Colour(WHITE))
        emb.set_footer(text="Example Command : g.winner 3 Discord Nitro")
        await ctx.send(embed = emb)

    @commands.command(aliases=['gw'])
    async def giveaway(self, ctx, *description):
        # Input Nothing but the Command
        if len(description) == 0:
            emb = discord.Embed(title="🎁 Giveaway!", description="```Yay, Giveaway!!!\n1. Insert the Description\n2. Insert How much Time until Announcement\n3. Insert how many people will win it.```", colour=discord.Colour(WHITE))
            emb.set_footer(text="Example Command : g.winner 3 Discord Nitro")
            await ctx.send(embed = emb)

        # if user need a Help about Giveaway
        if len(description) == 1 and (description[0].lower() == 'h' or description[0].lower() == 'help'):
            await self.help_giveaway(ctx)

        # Anything else
        else:
            try:
                handler_msg = await ctx.send(content="**Insert Duration (Duration : <mm ss\>) :**\n*You have 200 Seconds to reply this message.*")
                this_msg = await self.bot.wait_for(event='message', check=self.check_giveaway_duration(ctx.message.author), timeout=200.0)
                duration: int = self.convert_time_for_giveaway(this_msg.content)
                await this_msg.delete()
                await handler_msg.delete()
            except asyncio.TimeoutError:
                await ctx.send("*Request Time Out.*")
                await handler_msg.delete()
                return

            try:
                handler_msg1 = await ctx.send(content="**Insert Many People Win (Many : <num\>) :**\n*You have 200 Seconds to reply this message.*")
                this_msg1 = await self.bot.wait_for(event='message', check=self.check_giveaway_many_people(ctx.message.author), timeout=200.0)
                many_ppl = int(this_msg1.content)
                await this_msg1.delete()
                await handler_msg1.delete()
            except asyncio.TimeoutError:
                await ctx.send("*Request Time Out, Please try again later.*")
                await handler_msg1.delete()
                return

            threading.Thread(target=await self.co_gw(duration, ctx, " ".join(description), many_ppl)).start()

    @giveaway.error
    async def giveaway_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await self.help_giveaway(ctx)

    @commands.command()
    async def choose(self, ctx, *obj):
        choosen: str = random.choice(obj)
        emb = discord.Embed(title="I Choose",
        description=f"**{choosen}**",
        colour=discord.Colour(WHITE))
        await ctx.send(embed=emb)

def setup(bot):
    bot.add_cog(Choose(bot))