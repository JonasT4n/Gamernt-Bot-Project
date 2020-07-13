import os
import asyncio
import random
import discord
from discord.ext import commands, tasks
from Settings.MyUtility import get_prefix
from RPGPackage.RPGCharacter import checkClassID
from RPGPackage.RPGAttribute import *

WHITE = 0xfffffe

class Duel(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot    

    # Cooler Down

    cooldown: list = []

    async def _battle_finish(self, ids: int):
        self.cooldown.remove(ids)

    @tasks.loop(minutes= 2)
    async def empty_cooldown(self):
        if len(self.cooldown) == 0:
            pass
        else:
            self.cooldown.clear()

    # Event Listener Area

    @commands.Cog.listener()
    async def on_ready(self):
        self.empty_cooldown.start()

    @commands.Cog.listener()
    async def on_disconnect(self):
        self.cooldown.clear()
        self.empty_cooldown.cancel()

    # Gameplay Area

    async def fair_gameplay(self, channel: discord.TextChannel, p1: discord.User, p2: discord.User):
        # System Attribute
        emb = discord.Embed(title="⚔️", colour=WHITE)
        hm: discord.Message = await channel.send(embed=emb)
        container_log: list = []
        c1, c2 = checkClassID(p1), checkClassID(p2)
        max_hp_p1, max_hp_p2 = c1.HP, c2.HP
        
        # Duel Begins
        whos_first: int = 0 if c1.SPD > c2.SPD else (random.randint(0, 1) if c1.SPD == c2.SPD else 1)
        while c1.HP > 0 and c2.HP > 0:
            # Player One Make Move
            if whos_first == 0: 
                whos_first = 1
                typeAtt, rawDmg = c1.NormalAttack()
                dmg: int = c2.Defend(typeAtt, rawDmg)
                container_log.append(f"`{p1.name}` Hit `{p2.name}`, dealt **{dmg}** dmg")
                c2.HP = 0 if c2.HP <= 0 else c2.HP

            # Player Two Make Move
            else: 
                whos_first = 0
                typeAtt, rawDmg = c2.NormalAttack()
                dmg: int = c1.Defend(typeAtt, rawDmg)
                container_log.append(f"`{p2.name}` Hit `{p1.name}`, dealt **{dmg}** dmg")
                c1.HP = 0 if c1.HP <= 0 else c1.HP

            # Deleting Logs
            while len(container_log) > 3:
                container_log.pop(0)

            # Sending an Information Duel
            emb = discord.Embed(
                title="⚔️ Duel | On the Ring", 
                description=f"> **{p1.name}** ({c1.ClassName}) `HP: {c1.HP}/{c1.MAX_HP} | MN: {c1.MANA}/{c1.MAX_MANA}`\n"
                    f"> **{p2.name}** ({c2.ClassName}) `HP: {c2.HP}/{c2.MAX_HP} | MN: {c2.MANA}/{c2.MAX_MANA}`", 
                colour=WHITE
                )
            emb.add_field(
                name="Battle Log :", 
                value="\n".join(container_log), 
                inline=False
                )
            await hm.edit(embed=emb)
            await asyncio.sleep(1)
        
        # Duel final Result
        await asyncio.sleep(1)
        if c1.HP == 0:
            emb = discord.Embed(
                title="⚔️ Duel | Battle End", 
                description=f"> **{p1.name}** : Died\n"
                    f"> **{p2.name}** : {c2.HP} HP left\n"
                    f"`🏆 Congratulation {p2.name}!`",
                colour=WHITE
                )
            emb.set_thumbnail(url=p2.avatar_url)
        else:
            emb = discord.Embed(
                title="⚔️ Duel | Battle End", 
                description=f"> **{p1.name}**: {c1.HP} HP left\n"
                    f"> **{p2.name}**: Died\n"
                    f"`🏆 Congratulations {p1.name}!`", 
                colour=WHITE
                )
            emb.set_thumbnail(url=p1.avatar_url)
        emb.add_field(name="Battle Log:", value="\n".join(container_log), inline = False)
        await hm.edit(embed=emb)
        await self._battle_finish(channel.id)

    # Commands Area
        
    @commands.command(name="duel")
    async def _duel(self, ctx: commands.Context, *args):
        chnl: discord.TextChannel = ctx.channel
        if len(args) == 0:
            await self.print_help(ctx.channel)
        else:
            # Wait for Current ongoing duel finish
            if chnl.id in self.cooldown:
                hm: discord.Message = await ctx.send(f"*Duel In Progress in this Channel. ({chnl.name})*")
                await asyncio.sleep(3)
                await hm.delete()
                await ctx.message.delete()
            else:
                self.cooldown.append(chnl.id)
                async with ctx.typing():
                    person1: discord.User
                    person2: discord.User

                    # Start
                    if args[0].lower() == "-s" or args[0].lower() == "start":
                        person1 = ctx.author
                        person2 = self.search_user(ctx.guild)

                    # Random
                    elif args[0].lower() == "-r" or args[0].lower() == "random":
                        person1 = self.search_user(ctx.guild)
                        person2 = self.search_user(ctx.guild)

                    # Name or Tag
                    else:
                        user_id: int
                        if len(args) == 1 and "@!" in args[0]:
                            person1 = ctx.author
                            user_id = int(args[0].split('!')[1].split('>')[0])
                            person2 = self.bot.get_user(user_id)

                        elif "@!" not in " ".join(args):
                            person1 = ctx.author
                            person2 = self.search_user(ctx.guild, name= " ".join(args))

                        elif len(args) == 2 and "@!" in args[0] and "@!" in args[1]:
                            user_id = int(args[0].split('!')[1].split('>')[0])
                            person1 = self.bot.get_user(user_id)
                            user_id = int(args[0].split('!')[1].split('>')[0])
                            person2 = self.bot.get_user(user_id)
                    
                    # If the Player is the Same, Randomly pick other
                    if person1 is None or person2 is None:
                        if person1 is None:
                            person1 = self.search_user(ctx.guild)
                        if person2 is None:
                            person2 = self.search_user(ctx.guild)
                        while person1 == person2:
                            person2 = self.search_user(ctx.guild)

                    await self.fair_gameplay(chnl, person1, person2)

    # Others

    @staticmethod
    def search_user(guild: discord.Guild, *, name: str = None):
        list_of_user: list or tuple = guild.members
        if name is None:
            return random.choice(list_of_user)
        else:
            i: discord.Member
            for i in list_of_user:
                username = i.nick if i.nick is not None else i.name
                if name == username or name == i.name:
                    return i
            else:
                return random.choice(list_of_user)

    @staticmethod
    async def print_help(channel: discord.TextChannel):
        pref: str = get_prefix(channel.guild)
        emb = discord.Embed(title="⚔️ Auto Fair Duel Fight", colour=WHITE)
        emb.add_field(
            name="Command :",
            value=f"`{pref}duel <option>`",
            inline=False
            )
        emb.add_field(
            name="Options :",
            value="`[name]` - Challange this person\n"
                "`[@]` - Duel tagged person\n"
                "`[@] [@]` - Duel between 2 tags\n"
                "`-s`|`start` - Start fight you vs random person\n"
                "`-r`|`random` - Random 2 person",
            inline=False
            )
        emb.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Crossed_swords.svg/512px-Crossed_swords.svg.png")
        emb.set_footer(text=f"Example Command : {pref}duel @Gamern't Bot")
        await channel.send(embed=emb)

def setup(bot: commands.Bot):
    bot.add_cog(Duel(bot))