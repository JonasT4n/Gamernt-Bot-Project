import discord
from discord.ext import tasks, commands
from discord.utils import get
import asyncio, os, threading, datetime, time, random, re
from Settings.DbManager import DbManager as dbm
from Settings.Handler import *

WHITE = 0xfffffe

class PollGiveaway(commands.Cog):
    
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        
    @commands.command()
    async def poll(self, ctx, *emoji):
        try:
            if len(emoji) == 1 and (emoji[0].lower() == 'help' or emoji[0].lower() == 'h'):
                emb = discord.Embed(title="🗳️ Polling - Help", description="*For a Better Democracy!*", colour=discord.Colour(WHITE))
                emb.set_thumbnail(url="https://cdn.discordapp.com/attachments/588917150891114516/676383812565073920/PollThumb.png")
                emb.set_footer(text="Example Command : g.poll 👍🏻👎🏻")
                await ctx.send(embed=emb)
            else:
                all_emoji_list = []
                for emo in emoji:
                    if re.search("^<:.*:.*>", emo):
                        all_emoji_list.append(emo)
                    else:
                        s = emo.encode('unicode-escape').decode('ASCII')
                        if '\\U' in s:
                            all_emoji_list.append(emo)
                        else:
                            continue
                all_emoji_list = list(set(all_emoji_list))
                hnd_msg1 = await ctx.send(content="> Send a Title of This Poll Please, {}!".format(ctx.message.author.name))
                this_msg1 = await self.bot.wait_for(event="message", check=check_png_description_input(ctx.message.author), timeout=60.0)
                await hnd_msg1.delete()
                hnd_msg2 = await ctx.send(content="> Send a Description Please, {}!".format(ctx.message.author.name))
                this_msg2 = await self.bot.wait_for(event="message", check=check_png_description_input(ctx.message.author), timeout=60.0)
                await hnd_msg2.delete()
                # Making a Poll
                emb = discord.Embed(title=this_msg1.content, description=this_msg2.content, colour=discord.Colour(WHITE))
                emb.set_thumbnail(url="https://cdn.discordapp.com/attachments/588917150891114516/676387305002500116/PollBOI.png")
                emb.set_footer(text="Poll made on {}".format(datetime.datetime.now().date()))
                poll_msg = await ctx.send(embed=emb)
                for emo in all_emoji_list:
                    await poll_msg.add_reaction(emo)
                await this_msg1.delete()
                await this_msg2.delete()
        except Exception as exc:
            if type(exc) == asyncio.TimeoutError:
                await ctx.send("***Request Timeout!***")
            else:
                print(type(exc), exc)
                
    @poll.error
    async def poll_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            emb = discord.Embed(title="~ Poll Event ~ UNDER MAINTENANCE", colour=discord.Colour(WHITE))
            emb.set_footer(text="Command : g.poll <Emojis>")
            await ctx.send(embed=emb)
    
    @commands.command(aliases=['gw'])
    async def giveaway(self, ctx, *description):
        try:
            handler_msg = await ctx.send(content="**Insert Duration** (Duration : \<hh mm ss\>) :")
            this_msg = await self.bot.wait_for(event='message', check=check_png_times(ctx.message.author), timeout=120.0)
            await this_msg.delete()
            await handler_msg.delete()
            duration: int = convert_time_for_png(this_msg.content)
            handler_msg1 = await ctx.send(content="**Insert Many People Win (Many : <num\>) :**")
            this_msg1 = await self.bot.wait_for(event='message', check=check_png_many_people(ctx.message.author), timeout=120.0)
            many_ppl = int(this_msg1.content)
            await this_msg1.delete()
            await handler_msg1.delete()
            threading.Thread(target=await self.co_gw(duration, ctx, " ".join(description), many_ppl)).start()
        except asyncio.TimeoutError:
            await ctx.send("*Request Time Out, Please try again later.*")
        
    @giveaway.error
    async def giveaway_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            emb = discord.Embed(title="~ GIVEAWAY Event ~", colour=discord.Colour(WHITE))
            emb.set_footer(text="Example Command : g.giveaway 1000$")
            await ctx.send(embed=emb)
    
    async def co_gw(self, dur, ctx, desc, ppl: int):
        emb = discord.Embed(title="🎁 GIVEAWAY! 🎁", colour=discord.Colour(WHITE))
        emb.add_field(name="By {}".format(ctx.message.author.name), value="{}".format(desc), inline=False)
        emb.set_footer(text="Started on {} at {}; React this TADA to Join".format(datetime.datetime.now().date(), datetime.datetime.now().strftime("%H:%M:%S")))
        wait_msg = await ctx.send(embed=emb)
        await wait_msg.add_reaction(u"\U0001F389")
        await asyncio.sleep(dur)
        get_updated_msg = discord.utils.get(self.bot.cached_messages, id=wait_msg.id)
        all_ppl_joined = await get_updated_msg.reactions[0].users().flatten()
        del all_ppl_joined[0]
        winner = []
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
        emb = discord.Embed(colour=discord.Colour(WHITE))
        emb.add_field(name="🎁 Congratulation! 🎁", value="\n".join(winner), inline=False)
        emb.add_field(name="Award :", value="{}".format(desc), inline=False)
        await ctx.send(embed=emb)
    
def setup(bot):
    bot.add_cog(PollGiveaway(bot))