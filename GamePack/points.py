import discord
from discord.ext import commands, tasks
from Settings.DbManager import DbManager as dbm
from Settings.Handler import *
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
                self.data.cursor.execute("""SELECT * FROM point ORDER BY coins DESC LIMIT 100;""")
                list_user = self.data.cursor.fetchall()
                user_list, index_show = [], 0
                for u in range(len(list_user)):
                    person = self.bot.get_user(id=int(list_user[u][0]))
                    person_name = person.name.split('#')[0] + "#xxxx"
                    if (u + 1) % 20 == 0:
                        user_list.append("{}. **{}** {} Coins".format(u + 1, person_name, list_user[u][1]))
                    else:
                        user_list.append("{}. **{}** {} Coins\n".format(u + 1, person_name, list_user[u][1]))
                into_str = ""
                for ul in range(20 * index_show, 20 * (index_show + 1)):
                    into_str += user_list[ul]
                emb = discord.Embed(title="🌐 Global Leaderboard 🌐", description=into_str, colour=discord.Colour(WHITE))
                this_msg = await ctx.send(embed = emb)
                await this_msg.add_reaction("◀️")
                await this_msg.add_reaction("▶️")
                while index_show >= 0 and index_show < 5:
                    try:
                        await self.bot.wait_for(event="reaction_add", check=check_point_user_reaction(ctx.message.author, this_msg), timeout=60.0)
                    except asyncio.TimeoutError:
                        print("Timeout! No Reaction further more.")
            
        except Exception as exc:
            if type(exc) == AttributeError:
                print(type(exc), exc)
            else:
                print(type(exc), exc)
        
    @coin.error
    async def coin_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            self.data.cursor.execute("SELECT * FROM point WHERE id=:id", {"id":str(ctx.message.author.id)})
            info = self.data.cursor.fetchone()
            if info is None and ctx.message.author.bot is False:
                self.data.cursor.execute("INSERT INTO point VALUES (:id, :zero)", {"id":str(ctx.message.author.id), "zero":0})
                self.data.connect.commit()
                self.data.cursor.execute("SELECT * FROM point WHERE id=:id", {"id":str(ctx.message.author.id)})
                info = self.data.cursor.fetchone()
            emb = discord.Embed(title="{}'s Coin".format(ctx.message.author.name), description="**💰 {} Coin(s)**".format(info[1]), colour=discord.Colour(WHITE))
            await ctx.send(embed=emb)
        
def setup(bot):
    bot.add_cog(PointSystem(bot))