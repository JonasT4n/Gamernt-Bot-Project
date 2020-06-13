import os
import asyncio
import threading
import random
import re
import shutil
import requests
import math
import discord
from discord.ext import commands, tasks
from Settings.MyUtility import get_prefix, checkin_member, convert_rpg_substat

WHITE = 0xfffffe

class Duelist:

    HP: int = 800
    DEF: int = 100
    SPD: int = 10
    MIN_ATT: int = 120
    MAX_ATT: int = 150
    CRIT_CHANCE: int = 5

    def __init__(self, uid: int):
        mbr_data: dict = checkin_member(uid)
        if "MAX-STAT" in mbr_data:
            stat: dict = convert_rpg_substat(mbr_data["MAX-STAT"], return_value= True)
            self.HP = stat["HP"]
            self.DEF = stat["DEF"]
            self.SPD = stat["SPD"]
            self.MIN_ATT = stat["MIN-ATT"]
            self.MAX_ATT = stat["MAX-ATT"]
            self.CRIT_CHANCE = stat["CRIT"]

    def attack(self, target):
        """
        
        Parameters
        ---------
        target (Duelist) : Target Attack

        Returns
        -------
        (int) : Damage Dealt Information
        
        """
        att_multi = 1.2
        def_multi = 1
        spd_luck = random.randint(1, 100)
        if random.randint(1, 100) <= self.CRIT_CHANCE:
            att_multi += 0.8
        if spd_luck <= target.SPD:
            att_multi -= 1
        if spd_luck <= target.SPD // 3:
            att_multi = 0
        damage = math.ceil(random.randint(self.MIN_ATT, self.MAX_ATT) * att_multi * 100 / (100 + (target.DEF * def_multi)))
        target.HP -= damage
        return damage

class Duel(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Event Listener Area

    @commands.Cog.listener()
    async def on_ready(self):
        print("Fair Duel is Ready!")

    # Gameplay Area

    async def fair_gameplay(self, channel: discord.TextChannel, p1: discord.User, p2: discord.User):
        # Funny Description
        damage_dealt = [
            "{} punched {} hard. ({} dmg)", 
            "{} tripped {}'s leg and fall. ({} dmg)", 
            "{} kicked {} out of the ring. ({} dmg)", 
            "{} slashed {} with hand chop. ({} dmg)",
            "{} slapped {} his face. ({} dmg)",
            "{} tread {}'s toe hard. ({} dmg)",
            "{} knock {}'s Head off. ({} dmg)"
        ]

        # System Attribute
        emb = discord.Embed(
            title= "⚔️", 
            colour= discord.Colour(WHITE)
            )
        hm: discord.Message = await channel.send(embed = emb)
        container_log: list = []
        c1: Duelist = Duelist(p1.id)
        c2: Duelist = Duelist(p2.id)
        max_hp_p1: int = c1.HP
        max_hp_p2: int = c2.HP

        # Animation for first move pick
        whos_first: int = random.randint(0, 1)
        role_first: int = random.randint(4, 6)
        for a in range(role_first):
            if whos_first == 0:
                if a == role_first - 1:
                    emb = discord.Embed(
                        title= f"⚔️ {p1.name} got the first mov", 
                        colour= discord.Colour(WHITE)
                        )
                    await hm.edit(embed = emb)
                else:
                    emb = discord.Embed(
                        title= f"⚔️ {p1.name}", 
                        colour= discord.Colour(WHITE)
                        )
                    await hm.edit(embed = emb)
                    whos_first = 1
            else:
                if a == role_first - 1:
                    emb = discord.Embed(
                        title= f"⚔️ {p2.name} got the first move", 
                        colour= discord.Colour(WHITE)
                        )
                    await hm.edit(embed = emb)
                else:
                    emb = discord.Embed(
                        title= f"⚔️ {p2.name}", 
                        colour= discord.Colour(WHITE)
                        )
                    await hm.edit(embed = emb)
                    whos_first = 0
        await asyncio.sleep(1)
        
        # Duel Begins
        while c1.HP > 0 and c2.HP > 0:
            # Player One Make Move
            if whos_first == 0: 
                whos_first = 1
                dmg: int = c1.attack(c2)
                container_log.append(f"> {random.choice(damage_dealt).format(p1.name, p2.name, dmg)}")
                c2.HP = 0 if c2.HP <= 0 else c2.HP
            # Player Two Make Move
            else: 
                whos_first = 0
                dmg: int = c2.attack(c1)
                container_log.append(f"> {random.choice(damage_dealt).format(p2.name, p1.name, dmg)}")
                c1.HP = 0 if c1.HP <= 0 else c1.HP

            # Deleting Logs
            while len(container_log) > 5:
                container_log.pop(0)

            # Sending an Information Duel
            emb = discord.Embed(
                title = "⚔️ Duel | On the Ring", 
                description = f"> **{p1.name} HP** : {c1.HP} / {max_hp_p1}\n"
                    f"> **{p2.name} HP** : {c2.HP} / {max_hp_p2}", 
                colour = discord.Colour(WHITE)
                )
            emb.add_field(
                name = "Battle Log :", 
                value = "\n".join(container_log), 
                inline = False
                )
            await hm.edit(embed = emb)
            await asyncio.sleep(1)
        
        # Duel final Result
        await asyncio.sleep(1)
        if c1.HP == 0:
            emb = discord.Embed(
                title= "⚔️ Duel | Battle End", 
                description= f"> **{p1.name}** : Died\n> **{p2.name}** : {c2.HP} HP left\n`🏆 Congratulation {p2.name}!`",
                colour= discord.Colour(WHITE)
                )
        else:
            emb = discord.Embed(
                title= "⚔️ Duel | Battle End", 
                description= f"> **{p1.name}** : {c1.HP} HP left\n> **{p2.name}** : Died\n`🏆 Congratulations {p1.name}!`", 
                colour= discord.Colour(WHITE)
                )
        emb.add_field(name= "Battle Log :", value="\n".join(container_log), inline = False)
        emb.set_thumbnail(url= p1.avatar_url)
        await hm.edit(embed = emb)

    # Commands Area
        
    @commands.command()
    async def duel(self, ctx: commands.Context, *args):
        person1: discord.User
        person2: discord.User
        if len(args) == 0:
            await self.print_help(ctx.channel)
        else:
            if args[0].lower() == "-s" or args[0].lower() == "start":
                person1 = ctx.author
                person2 = self.search_user(ctx.guild)
                while person1 == person2:
                    person2 = self.search_user(ctx.guild)

            elif args[0].lower() == "-h" or args[0].lower() == "help":
                await self.print_help(ctx.channel)
                return

            elif args[0].lower() == "-r" or args[0].lower() == "random":
                person1 = self.search_user(ctx.guild)
                person2 = self.search_user(ctx.guild)

            else:
                if len(args) >= 1 and "@!" in args[0]:
                    person1 = ctx.author
                    user_id: int = int(args[0].split('!')[1].split('>')[0])
                    person2 = await self.bot.get_user(user_id)

                elif len(args) >= 1:
                    person1 = ctx.author
                    person2 = self.search_user(ctx.guild, name = args[0])

                elif len(args) >= 2 and "@!" in args[0] and "@!" in args[1]:
                    user_id: int = int(args[0].split('!')[1].split('>')[0])
                    person1 = await self.bot.get_user(user_id)
                    user_id: int = int(args[0].split('!')[1].split('>')[0])
                    person2 = await self.bot.get_user(user_id)

            while person1 == person2:
                person2 = self.search_user(ctx.guild)

            await self.fair_gameplay(ctx.channel, person1, person2)

    # Others

    @staticmethod
    def search_user(guild: discord.Guild, *, name: str = None):
        list_of_user: list or tuple = guild.members
        if name is None:
            return random.choice(list_of_user)
        else:
            i: discord.Member
            for i in list_of_user:
                if name in i.nick or name in i.display_name:
                    return i
            else:
                return random.choice(list_of_user)

    @staticmethod
    async def print_help(channel: discord.TextChannel):
        pref: str = get_prefix(channel.guild.id)
        emb = discord.Embed(
            title= "⚔️ Fair Duel Fight", 
            colour= discord.Colour(WHITE)
        )
        emb.add_field(
            name= "Command :",
            value= f"`{pref}duel <option>`",
            inline= False
        )
        emb.add_field(
            name= "Options :",
            value= "> `[name]` - Challange this person\n"
                "> `[@]` - Duel tagged person\n"
                "> `[@] [@]` - Duel between 2 tags\n"
                "> -s (start) - Start fight you vs random person\n"
                "> -h (help) - Help duel command\n"
                "> -r (random) - Random 2 person",
            inline= False
        )
        emb.set_thumbnail(url= "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Crossed_swords.svg/512px-Crossed_swords.svg.png")
        emb.set_footer(text= f"Example Command : {pref}duel @Gamern't Bot")
        await channel.send(embed = emb)

def setup(bot: commands.Bot):
    bot.add_cog(Duel(bot))