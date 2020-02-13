import discord
from discord.ext import commands, tasks
import os, asyncio, threading, random, re

WHITE = 0xfffffe

class Duel(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def duel(self, ctx, person1 = None, person2 = None):
        try:
            if person1 is None and person2 is None:
                person1 = ctx.message.author
                person2 = random.choice(ctx.message.guild.members)
                threading.Thread(target=await self.begins(person1, person2)).start()
            elif person1.lower() == 'help' or person1.lower() == 'h':
                emb = discord.Embed(title="⚔️ Duel Fight", description="Punch, Kick, and Kill your friend. Nothing Else!", colour=discord.Colour(WHITE))
                emb.set_thumbnail(url="https://cdn.discordapp.com/attachments/588917150891114516/676351507322503168/VSBattle_Logo.png")
                emb.add_field(name="Command (alias):", value="***Coming Soon!!!***", inline=False)
                emb.set_footer(text="Example Command : g.duel [Tag your Friend]")
        except Exception as exc:
            print(type(exc), exc)
    
    @duel.error
    async def duel_error(self, ctx, error):
        pass

    async def begins(self, p1, p2):
        pass
    
def setup(bot):
    bot.add_cog(Duel(bot))