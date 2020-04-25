import discord
from discord.ext import tasks, commands
from discord.utils import get
import asyncio, os, threading, datetime, time, random, re
from Settings.DbManager import DbManager as dbm
from Settings.Handler import *

WHITE = 0xfffffe

class PollGiveaway(commands.Cog):

    thumbnails: list = [
        "https://wdwnt.com/wp-content/uploads/2017/06/take-a-wdwnt-poll-for-a-chance-to-win-a-disney-prize-package.png",
        "https://cdn.discordapp.com/attachments/588917150891114516/676383812565073920/PollThumb.png",
        "https://icons.iconarchive.com/icons/iconarchive/blue-election/1024/Election-Polling-Box-01-Outline-icon.png"
    ]
    
    def __init__(self, bot):
        self.bot = bot

    def check_poll_description_input(self, author):
        def inner_check(message):
            if author == message.author and len(message.content) <= 1024:
                return True
            else:
                return False
        return inner_check

    async def help_poll(self, ctx):
        emb = discord.Embed(title="🗳️ Polling - Help", description="*For a Better Democracy!*", colour=discord.Colour(WHITE))
        emb.set_thumbnail(url = random.choice(self.thumbnails))
        emb.set_footer(text="Example Command : g.poll Best Gamer 2020")
        await ctx.send(embed=emb)
        
    @commands.command()
    async def poll(self, ctx, *title):
        if title[0].lower() == 'help' or title[0].lower() == 'h':
            await self.help_poll(ctx)
            
        else:
            try:
                emb = discord.Embed(title="Type the Description : ", description="*You have 200 Second to write the Description.*", colour=discord.Colour(WHITE))
                this_bot_msg = await ctx.send(embed=emb)
                reply = await self.bot.wait_for(event="message", check=self.check_poll_description_input(ctx.message.author), timeout=200.0)
                await this_bot_msg.delete()
            except asyncio.TimeoutError:
                await this_bot_msg.delete()
                await ctx.send("***Request Timeout!***")
                return

            emb = discord.Embed(title="🗳️" + " ".join(title), description=reply.content, colour=discord.Colour(WHITE))
            emb.set_thumbnail(url = random.choice(self.thumbnails))
            emb.set_footer(text="React this Poll.")
            await ctx.send(embed=emb)
    
def setup(bot):
    bot.add_cog(PollGiveaway(bot))