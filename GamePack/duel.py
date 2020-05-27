import discord
from discord.ext import commands, tasks
import os
import asyncio
import threading
import random
import re
import shutil
import requests
from Settings.MyUtility import checkin_member
from Settings.MongoManager import MongoManager

WHITE = 0xfffffe

class Brawler:

    HP: int = 100 # Health Point of Player
    MAXDMG: int = 40 # Player can Hit until 40
    MINDMG: int = 25 # Player Minimal Damage is 25
    ARMOR: int = 23 # Player Defense Armor is 25, cutting the damage point

    def __init__(self, ppl: discord.User):
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
        self.mongodbm = MongoManager(collection="members")

    # Listener Area

    # Checker Area

    # Gameplay

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
            emb = discord.Embed(
                title="⚔️ Fair Duel ⚔️", 
                description="> **{}'s HP** : {}\n> **{}'s HP** : {}".format(p1name, p1.HP, p2name, p2.HP), 
                colour=discord.Colour(WHITE)
            )
            emb.add_field(name="Battle Log :", value="\n".join(container_log), inline=False)
            await handler_msg.edit(embed = emb)
            await asyncio.sleep(1)
        
        # Duel final Result
        await asyncio.sleep(3)
        if p1.HP == 0:
            emb = discord.Embed(
                title="⚔️ Duel Ended ⚔️", 
                description=f"> **{p1name}** : Died\n> **{p2name}** : {p2.HP} HP left\n`🏆 Congratulation {p2name}!`",
                colour=discord.Colour(WHITE)
            )
            emb.add_field(name="Battle Log :", value="\n".join(container_log), inline=False)
            emb.set_thumbnail(url=p2.p.avatar_url)
            await handler_msg.edit(embed = emb)
            self.get_point(p2.p, p1.p)
        else:
            emb = discord.Embed(
                title="⚔️ Duel Ended ⚔️", 
                description=f"> **{p1name}** : {p1.HP} HP left\n> **{p2name}** : Died\n`🏆 Congratulations {p1name}!`", 
                colour=discord.Colour(WHITE)
            )
            emb.add_field(name="Battle Log :", value="\n".join(container_log), inline=False)
            emb.set_thumbnail(url=p1.p.avatar_url)
            await handler_msg.edit(embed = emb)
            self.get_point(p1.p, p2.p)

    # Commands Area
        
    @commands.command()
    async def duel(self, ctx: commands.Context, *args):
        person1: discord.User
        person2: discord.User

        if len(args) == 0:
            person1 = ctx.author
            person2 = random.choice(ctx.guild.members)
        else:
            if args[0] == "-random":
                person1 = random.choice(ctx.guild.members)
                person2 = random.choice(ctx.guild.members)

            elif args[0] == '-h':
                await self.print_help(ctx.channel)
                return

            elif len(args) == 1:
                person1 = ctx.author
                if re.search("^<@\S*>$", person1):
                    person2 = self.bot.get_user(int(person2.split('!')[1].split('>')[0]))
                else:
                    for mbr in ctx.guild.members:
                        if person1.lower() in mbr.name.lower():
                            person2 = mbr
                            break
                    else:
                        person2 = random.choice(ctx.guild.members)

            elif len(args) == 2:
                if re.search("^<@\S*>$", person1) and re.search("^<@\S*>$", person2):
                    person1 = self.bot.get_user(int(person1.split('!')[1].split('>')[0]))
                    person2 = self.bot.get_user(int(person2.split('!')[1].split('>')[0]))
                elif re.search("^<@\S*>$", person1) and not re.search("^<@\S*>$", person2):
                    person1 = self.bot.get_user(int(person1.split('!')[1].split('>')[0]))
                    person2 = random.choice(ctx.guild.members)
                elif not re.search("^<@\S*>$", person1) and re.search("^<@\S*>$", person2):
                    person1 = random.choice(ctx.guild.members)
                    person2 = self.bot.get_user(int(person2.split('!')[1].split('>')[0]))
                else:
                    person1 = random.choice(ctx.guild.members)
                    person2 = random.choice(ctx.guild.members)

        while person1 == person2:
            person2 = random.choice(ctx.guild.members)
        await self.begins(ctx.channel, Brawler(person1), Brawler(person2))

    # Commands Error Handler

    @duel.error
    async def _duel_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            emb = discord.Embed(
                title="💤 Tired 💤", 
                description="Next round can be held in {0:.2f} s".format(error.retry_after), 
                colour=discord.Colour(WHITE)
            )
            await ctx.send(embed=emb)

    # Others

    def get_point(self, winner: discord.User, loser: discord.User):
        # Init Variables
        winner_data: dict
        loser_data: dict

        # Winner Result
        if winner.bot is False:
            self.mongodbm.IncreaseItem({"member_id": str(winner.id)}, {"trophy": self.winner_get})

        # Loser Result
        if loser.bot is False:
            loser_data: dict = checkin_member(loser.id)
            loser_data["trophy"] -=  self.loser_lost
            if loser_data["trophy"] < 0:
                loser_data["trophy"] = 0
            self.mongodbm.SetObject({"member_id": str(loser.id)}, {"trophy": loser_data["trophy"]})

    @staticmethod
    async def print_help(channel: discord.TextChannel):
        emb = discord.Embed(
            title="⚔️ Fair Duel Fight", 
            description=open("./Help/duelh.txt").read(), 
            colour=discord.Colour(WHITE)
        )
        emb.set_footer(text="Example Command : g.duel @Gamern't Bot")
        await channel.send(embed = emb)

def setup(bot):
    bot.add_cog(Duel(bot))