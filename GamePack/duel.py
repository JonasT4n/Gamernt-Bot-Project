import discord
from discord.ext import commands, tasks
import os, asyncio, threading, random, re
import shutil
import requests

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
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def duel(self, ctx, person1 = None, person2 = None):
        try:
            if person1 is None and person2 is None:
                person1 = ctx.message.author
                person2 = random.choice(ctx.message.guild.members)
                await self.begins(ctx.message.channel, Brawler(person1), Brawler(person2))
            elif person1 == "random" or person1 == "rdm":
                person1 = random.choice(ctx.message.guild.members)
                person2 = random.choice(ctx.message.guild.members)
                await self.begins(ctx.message.channel, Brawler(person1), Brawler(person2))
            elif person1.lower() == 'help' or person1.lower() == 'h':
                emb = discord.Embed(title="⚔️ Duel Fight", description="Punch, Kick, and Kill your friend. Nothing Else!", colour=discord.Colour(WHITE))
                emb.set_thumbnail(url="https://cdn.discordapp.com/attachments/588917150891114516/676351507322503168/VSBattle_Logo.png")
                emb.add_field(name="Command (alias):", value=open("./DataPack/Help/duelh.txt", 'r').read(), inline=False)
                emb.add_field(name="Others :", value="> You can Duel your Friend without tagging them. Just Enter their Name.")
                emb.set_footer(text="Example Command : g.duel @Gamern't Bot")
                await ctx.send(embed = emb)
            elif person1 is not None and person2 is None:
                if re.search("^<@\S*>$", person1):
                    person2 = person1
                    person1 = ctx.message.author
                    person2 = self.bot.get_user(int(person2.split('!')[1].split('>')[0]))
                    await self.begins(ctx.message.channel, Brawler(person1), Brawler(person2))
                else:
                    for mbr in ctx.message.guild.members:
                        if person1 in mbr.name:
                            person2 = mbr
                            break
                    else:
                        person2 = random.choice(ctx.message.guild.members)
                    person1 = ctx.message.author
                    await self.begins(ctx.message.channel, Brawler(person1), Brawler(person2))
            elif person1 is not None and person2 is not None:
                pass
        except Exception as exc:
            print(type(exc), exc)

    async def begins(self, chnl, p1: Brawler, p2: Brawler):
        damage_dealt = ["*{} Punches {} on his Cheekbone.* ***({} dmg)***", "*{} Tripped {} onto the Ground.* ***({} dmg)***", "*{} kicked {} out of the arena.* ***({} dmg)***", "*{} slashed {} with chair.* ***({} dmg)***"]
        whos_first: int = random.randint(0, 1)
        p1name: str; p2name: str
        p1name, p2name = p1.p.name.split('#')[0], p2.p.name.split('#')[0]
        emb = discord.Embed(title="⚔️", colour=discord.Colour(WHITE))
        handler_msg, container_log = await chnl.send(embed=emb), []
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
        await asyncio.sleep(3)
        if p1.HP == 0:
            emb = discord.Embed(title="⚔️ Duel ⚔️".format(p2name), description="> **{}** : Died\n> **{}** : 🏆 The Champion!".format(p1name, p2name), colour=discord.Colour(WHITE))
            emb.add_field(name="Battle Log :", value="\n".join(container_log), inline=False)
            emb.set_thumbnail(url=p2.p.avatar_url)
            await handler_msg.edit(embed = emb)
            return p2.p
        else:
            emb = discord.Embed(title="⚔️ Duel ⚔️".format(p1name), description="> **{}** : 🏆 The Champion!\n> **{}** : Died".format(p1name, p2name), colour=discord.Colour(WHITE))
            emb.add_field(name="Battle Log :", value="\n".join(container_log), inline=False)
            emb.set_thumbnail(url=p1.p.avatar_url)
            await handler_msg.edit(embed = emb)
            return p1.p

def setup(bot):
    bot.add_cog(Duel(bot))