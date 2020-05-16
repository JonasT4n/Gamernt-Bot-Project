import discord
from discord.ext import commands, tasks
import os
import asyncio
import threading
import random
import re
import shutil
import requests
from Settings.MongoManager import MongoManager, new_member_data
from Settings.setting import MONGO_ADDRESS, DB_NAME

WHITE = 0xfffffe

class Brawler:

    HP: int = 100 # Health Point of Player
    MAXDMG: int = 43 # Player can Hit until 40
    MINDMG: int = 27 # Player Minimal Damage is 25
    ARMOR: int = 23 # Player Defense Armor is 25, cutting the damage point

    def __init__(self, ppl):
        self.p = ppl

    def attack(self):
        if self.HP < 65:
            self.MAXDMG = self.MAXDMG + random.randint(0, 2)
        return random.randint(self.MINDMG, self.MAXDMG)

    def defend(self):
        return self.ARMOR

class Duel(commands.Cog):

    winner_get: int = 3
    loser_lost: int = 2
    
    def __init__(self, bot):
        self.bot = bot
        self.mongodbm = MongoManager(MONGO_ADDRESS, DB_NAME)
        self.mongodbm.ConnectCollection("members")

    async def begins(self, chnl, p1: Brawler, p2: Brawler):
        # Funny Description
        damage_dealt = [
            "*{} punches {}.* ***({} dmg)***", 
            "*{} tripped {}.* ***({} dmg)***", 
            "*{} kicked {}.* ***({} dmg)***", 
            "*{} slashed {}.* ***({} dmg)***",
            "*{} slapped {}.* ***({} dmg)***",
            "*{} shooted {}.* ***({} dmg)***"
        ]

        # System Attribute
        whos_first: int = random.randint(0, 1)
        p1name: str = p1.p.name.split('#')[0]
        p2name: str = p2.p.name.split('#')[0]
        emb = discord.Embed(title="⚔️", colour=discord.Colour(WHITE))
        handler_msg = await chnl.send(embed=emb)
        container_log = []
        
        # Duel Begins
        while p1.HP > 0 and p2.HP > 0:
            # Making Turn and Battle
            if whos_first == 0: # Player One Make Move
                whos_first = 1
                damage: int = p1.attack() - p2.defend()
                container_log.append("> " + random.choice(damage_dealt).format(p1name, p2name, damage))
                p2.HP -= damage
                if p2.HP < 0:
                    p2.HP = 0
            else: # Player Two Make Move
                whos_first = 0
                damage: int = p2.attack() - p1.defend()
                container_log.append("> " + random.choice(damage_dealt).format(p2name, p1name, damage))
                p1.HP -= damage
                if p1.HP < 0:
                    p1.HP = 0
            # Deleting Logs
            while len(container_log) > 3:
                container_log.pop(0)
            # Sending an Information Duel
            emb = discord.Embed(title="⚔️ Duel ⚔️", description="> **{}'s HP** : {}\n> **{}'s HP** : {}".format(p1name, p1.HP, p2name, p2.HP), colour=discord.Colour(WHITE))
            emb.add_field(name="Battle Log :", value="\n".join(container_log), inline=False)
            await handler_msg.edit(embed = emb)
            await asyncio.sleep(1)
        
        # Duel final Result
        await asyncio.sleep(3)
        if p1.HP == 0:
            emb = discord.Embed(title="⚔️ Duel Ended ⚔️", description="> **{}** : Died\n> **{}** : {} HP left\n`🏆 Congratulation {}!`".format(p1name, p2name, p2.HP, p2name), colour=discord.Colour(WHITE))
            emb.add_field(name="Battle Log :", value="\n".join(container_log), inline=False)
            emb.set_thumbnail(url=p2.p.avatar_url)
            await handler_msg.edit(embed = emb)
            threading.Thread(target=self.get_point(p2.p, p1.p)).start()
        else:
            emb = discord.Embed(title="⚔️ Duel Ended ⚔️", description="> **{}** : {} HP left\n> **{}** : Died\n`🏆 Congratulations {}!`".format(p1name, p1.HP, p2name, p1name), colour=discord.Colour(WHITE))
            emb.add_field(name="Battle Log :", value="\n".join(container_log), inline=False)
            emb.set_thumbnail(url=p1.p.avatar_url)
            await handler_msg.edit(embed = emb)
            threading.Thread(target=self.get_point(p1.p, p2.p)).start()

    def checkin_member(self, person_id: int) -> dict:
        """
        
        Check if Member is in the Database.

            Returns :
                (dict) => Member Information
        
        """
        query: dict = {"member_id":str(person_id)}
        u_data = self.mongodbm.FindObject(query)
        if u_data is None:
            nd: dict = new_member_data
            nd["member_id"] = str(person_id)
            self.mongodbm.InsertOneObject(nd)
            u_data = self.mongodbm.FindObject(query)
        return u_data[0]

    def get_point(self, winner: discord.User, loser: discord.User):
        winner_data: dict
        loser_data: dict
        if winner.bot is False:
            winner_data = self.checkin_member(winner.id)
            winner_data["trophy"] += self.winner_get
            self.mongodbm.UpdateOneObject({"member_id": str(winner.id)}, winner_data)
        if loser.bot is False:
            loser_data = self.checkin_member(loser.id)
            loser_data["trophy"] -=  self.loser_lost
            if loser_data["trophy"] < 0:
                loser_data["trophy"] = 0
            self.mongodbm.UpdateOneObject({"member_id": str(loser.id)}, loser_data)
        
    @commands.command()
    async def duel(self, ctx, person1 = None, person2 = None):
        if person1 is None and person2 is None:
            person1 = ctx.message.author
            person2 = random.choice(ctx.message.guild.members)

        elif person1 == "random" or person1 == "rdm":
            person1 = random.choice(ctx.message.guild.members)
            person2 = random.choice(ctx.message.guild.members)

        elif person1.lower() == 'help' or person1.lower() == 'h':
            emb = discord.Embed(title="⚔️ Duel Fight", description="Punch, Kick, and Kill your friend", colour=discord.Colour(WHITE))
            emb.set_thumbnail(url="https://cdn.discordapp.com/attachments/588917150891114516/676351507322503168/VSBattle_Logo.png")
            emb.add_field(name="Command (alias):", value=open("./DataPack/Help/duelh.txt", 'r').read(), inline=False)
            emb.add_field(name="Others :", value="> You can Duel your Friend without tagging them. Just Enter their Name.")
            emb.set_footer(text="Example Command : g.duel @Gamern't Bot")
            await ctx.send(embed = emb)
            return

        elif person1 is not None and person2 is None:
            if re.search("^<@\S*>$", person1):
                person2 = person1
                person1 = ctx.message.author
                person2 = self.bot.get_user(int(person2.split('!')[1].split('>')[0]))
            else:
                for mbr in ctx.message.guild.members:
                    if person1.lower() in mbr.name.lower():
                        person2 = mbr
                        break
                else:
                    person2 = random.choice(ctx.message.guild.members)
                person1 = ctx.message.author

        elif person1 is not None and person2 is not None:
            if re.search("^<@\S*>$", person1) and re.search("^<@\S*>$", person2):
                person1 = self.bot.get_user(int(person1.split('!')[1].split('>')[0]))
                person2 = self.bot.get_user(int(person2.split('!')[1].split('>')[0]))
            elif re.search("^<@\S*>$", person1) and not re.search("^<@\S*>$", person2):
                person1 = self.bot.get_user(int(person1.split('!')[1].split('>')[0]))
                person2 = random.choice(ctx.message.guild.members)
            elif not re.search("^<@\S*>$", person1) and re.search("^<@\S*>$", person2):
                person1 = random.choice(ctx.message.guild.members)
                person2 = self.bot.get_user(int(person2.split('!')[1].split('>')[0]))
            else:
                person1 = random.choice(ctx.message.guild.members)
                person2 = random.choice(ctx.message.guild.members)

        while person1 == person2:
            person2 = random.choice(ctx.message.guild.members)
        await self.begins(ctx.message.channel, Brawler(person1), Brawler(person2))

    @duel.error
    async def _duel_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            emb = discord.Embed(title="💤 Tired 💤", description="Next round can be held in {0:.2f} s".format(error.retry_after), colour=discord.Colour(WHITE))
            this_msg_coroute = await ctx.send(embed=emb)
            await asyncio.sleep(3)
            await this_msg_coroute.delete()

def setup(bot):
    bot.add_cog(Duel(bot))