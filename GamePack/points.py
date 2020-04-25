import discord
import asyncio
import os 
import random
from discord.ext import commands, tasks
from Settings.DbManager import DbManager as dbm
from Settings.Handler import *

WHITE = 0xfffffe

class PointSystem(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.db = dbm.connect_db("./DataPack/guild.db")

    def check_point_user_reaction(self, author, msg):
        def inner_check(reaction, user):
            if str(user.id) == str(author.id) and (str(reaction.emoji) == '▶️' or str(reaction.emoji) == '◀️'):
                return True
            else:
                return False
        return inner_check

    async def help_coin(self, ctx):
        emb = discord.Embed(title="💰 Coin Help", description="Might Be Usefull in the Future, **Stay Tune!**", colour=discord.Colour(WHITE))
        emb.add_field(name="Commands (alias):", value=open("./DataPack/Help/points.txt").read(), inline=False)
        await ctx.send(embed=emb)
        
    @commands.command(aliases=['cur'])
    async def currency(self, ctx, *, stat: str, person: discord.User = None):
        if stat.lower() == 'h' or stat.lower() == 'help': # Help About Point System
            await self.help_coin(ctx)

        elif person is not None:
            if not self.db.CheckExistence("coin", f"id={str(person.id)}"):
                self.db.InsertData("coin", id=str(person.id), coins=0)
            self.db.SelectRowData("coin", f"id={str(person.id)}")
            info = self.db.cursor.fetchone()
            emb = discord.Embed(title="{}'s Coin".format(person.name), description=f"**💰 {info[1]} Coin(s)**", colour=discord.Colour(WHITE))
            await ctx.send(embed=emb)
            
        elif stat.lower() == 'leaderboard' or stat.lower() == 'lb':
            self.db.cursor.execute("""SELECT m.member_id, c.coins FROM member m INNER JOIN coin c ON m.member_id = c.id WHERE m.server_id = :sid ORDER BY c.coins DESC LIMIT 5;
            """, {"sid":str(ctx.message.guild.id)})
            data = self.db.cursor.fetchall()
            nnc = [[self.bot.get_user(int(idmbr[0])).name, idmbr[1]] for idmbr in data]

            desc: str
            if len(nnc) < 5:
                if len(nnc) == 0:
                    desc = f"""```No One Yet Recorded :v```"""
                elif len(nnc) == 1:
                    desc = f"""```1. {nnc[0][0]} - {nnc[0][1]} 💸```"""
                elif len(nnc) == 2:
                    desc = f"""```1. {nnc[0][0]} - {nnc[0][1]} 💸\n2. {nnc[1][0]} - {nnc[1][1]} 💸```"""
                elif len(nnc) == 3:
                    desc = f"""```1. {nnc[0][0]} - {nnc[0][1]} 💸\n2. {nnc[1][0]} - {nnc[1][1]} 💸\n3. {nnc[2][0]} - {nnc[2][1]} 💸```"""
                elif len(nnc) == 4:
                    desc = f"""```1. {nnc[0][0]} - {nnc[0][1]} 💸\n2. {nnc[1][0]} - {nnc[1][1]} 💸\n3. {nnc[2][0]} - {nnc[2][1]} 💸\n4. {nnc[3][0]} - {nnc[3][1]} 💸```"""
            else:
                desc = f"""```1. {nnc[0][0]} - {nnc[0][1]} 💸\n2. {nnc[1][0]} - {nnc[1][1]} 💸\n3. {nnc[2][0]} - {nnc[2][1]} 💸\n4. {nnc[3][0]} - {nnc[3][1]} 💸\n5. {nnc[4][0]} - {nnc[4][1]} 💸```"""
            emb = discord.Embed(title="📋 Top 5 Server Leaderboard", description=desc, colour=discord.Colour(WHITE))
            await ctx.send(embed=emb)

        elif stat is None:
            if not self.db.CheckExistence("coin", f"id={str(ctx.message.author.id)}"):
                self.db.InsertData("coin", id=str(ctx.message.author.id), coins=0)
            self.db.SelectRowData("coin", f"id={str(ctx.message.author.id)}")
            info = self.db.cursor.fetchone()
            emb = discord.Embed(title=f"{ctx.message.author.name}'s Coin", description=f"**💰 {info[1]} Coin(s)**", colour=discord.Colour(WHITE))
            await ctx.send(embed=emb)

def setup(bot):
    bot.add_cog(PointSystem(bot))