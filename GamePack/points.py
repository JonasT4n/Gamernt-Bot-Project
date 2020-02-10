import discord
from discord.ext import commands, tasks
from Settings.DbManager import DbManager as dbm
import asyncio, os, random, re

WHITE = 0xfffffe

class PointSystem(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.data = dbm.connect_db("./DataPack/member.db")
        
    @commands.command()
    async def coin(self, ctx, stat: str):
        try:
            if re.search("^<@\S*>$", stat):
                stat = ctx.message.guild.get_member(int(stat.split('@')[1].split('>')[0]))
                self.data.cursor.execute("SELECT * FROM point WHERE id=:id", {"id":str(stat.id)})
                info = self.data.cursor.fetchone()
                if info is None and stat.bot is False:
                    self.data.cursor.execute("INSERT INTO point VALUES (:id, :zero)", {"id":str(stat.id), "zero":0})
                    self.data.connect.commit()
                    self.data.cursor.execute("SELECT * FROM point WHERE id=:id", {"id":str(stat.id)})
                    info = self.data.cursor.fetchone()
                emb = discord.Embed(title="{}'s Coin".format(stat.name), description="**💰 {} Coin(s)**".format(info[1]), colour=discord.Colour(WHITE))
                await ctx.send(embed=emb)
                
            if stat.lower() == 'h' or stat.lower() == 'help': # Help About Point System
                emb = discord.Embed(title="💰 Coin Help", description="Might Be Usefull in the Future, **Stay Tune!**", colour=discord.Colour(WHITE))
                emb.add_field(name="Commands (alias):", value=open("./DataPack/points.txt").read(), inline=False)
                await ctx.send(embed=emb)
                
            if stat.lower() == 'leaderboard' or stat.lower() == 'lb':
                pass
            
            if stat.lower() == 'global':
                pass
            
        except Exception as exc:
            if type(exc) == AttributeError:
                pass
            else:
                print(type(exc), exc)
        
    @coin.error
    async def coin_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            self.data.cursor.execute("SELECT * FROM point WHERE id=:id", {"id":str(ctx.message.author.id)})
            info = self.data.cursor.fetchone()
            if info is None and stat.bot is False:
                self.data.cursor.execute("INSERT INTO point VALUES (:id, :zero)", {"id":str(ctx.message.author.id), "zero":0})
                self.data.connect.commit()
                self.data.cursor.execute("SELECT * FROM point WHERE id=:id", {"id":str(ctx.message.author.id)})
                info = self.data.cursor.fetchone()
            emb = discord.Embed(title="{}'s Coin".format(ctx.message.author.name), description="**💰 {} Coin(s)**".format(info[1]), colour=discord.Colour(WHITE))
            await ctx.send(embed=emb)
        
def setup(bot):
    bot.add_cog(PointSystem(bot))