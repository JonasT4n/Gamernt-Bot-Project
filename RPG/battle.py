import discord
import math
import random
import asyncio
from discord.ext import commands
from Settings.MongoManager import MongoManager
from Settings.MyUtility import checkin_member, get_prefix, is_number
from RPGPackage.RPGCharacter import *

WHITE = 0xfffffe

RewardMoney: int = 2000
RewardEXP: int = 50

class Teams:

    _id: int = 0

    @property
    def id(self):
        return self._id

class Battle(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.mdb = MongoManager(collection="members")
        self.gdb = MongoManager(collection="guilds")

    # Cooler Down

    cooldown: list = []

    async def _cooling_down(self, ids: int):
        self.cooldown.remove(ids)

    # Command Area

    @commands.command(name= "battle", aliases= ['btl'], pass_context= True)
    async def _battle(self, ctx: commands.Context, *args):
        chnl: discord.TextChannel = ctx.channel
        mbr_data: dict = checkin_member(ctx.author.id)
        if "PRIM-STAT" in mbr_data:
            if len(args) == 0:
                await self.print_help(ctx.channel)
            else:
                if chnl.id in self.cooldown:
                    hm: discord.Message = await ctx.send(f"*Battle in Progress in this Channel. ({chnl.name})*")
                    await asyncio.sleep(3)
                    await hm.delete()
                    await ctx.message.delete()
                else:
                    self.cooldown.append(chnl.id)

                    # 1 vs 1 Battle
                    if args[0].lower() == "1v1":
                        await self._queue(ctx, 2)

                    # 2 vs 2 Battle
                    elif args[0].lower() == "2v2":
                        await self._queue(ctx, 4)

                    # 3 vs 3 Battle
                    elif args[0].lower() == "3v3":
                        await self._queue(ctx, 6)
        else:
            await ctx.send(f"__**{ctx.author.name}, You haven't start your character, type {get_prefix(ctx.guild.id)}start to begin.**__")

    # Queue

    async def _queue(self, context: commands.Context, player_count: int):
        # Send Hint
        channel: discord.TextChannel = context.channel
        teams: list = ["🔴", "🔵"]
        async with channel.typing():
            team1, team2 = [], []
            max_pcount: int = player_count // 2
            emb = discord.Embed(
                title="⌛ Waiting for Other Player to Join...",
                description=f"{max_pcount}v{max_pcount} mode",
                colour=WHITE
                )
            emb.add_field(
                name="🔴 Red Team",
                value="```Empty Room```",
                inline=False
                )
            emb.add_field(
                name="🔵 Blue Team",
                value="```Empty Room```",
                inline=False
                )
            emb.set_footer(text="React to Join One of the Team 🔴 🔵")
        hm: discord.Message = await channel.send(embed=emb)
        for i in teams:
            await hm.add_reaction(i)

        # Edit Hint and Wait for User
        try:
            while True:
                # Wait for Reaction Reply
                r: discord.Reaction
                u: discord.User
                r, u = await self.bot.wait_for(
                    event= "reaction_add",
                    check= lambda reaction, user: True if str(reaction.emoji) in teams and user.bot is False else False,
                    timeout= 60.0
                    )

                # On Join Check
                footer_text: str
                if str(r.emoji) == "🔴":
                    if len(team1) == max_pcount:
                        footer_text = "Party Already Full"
                    else:
                        if u.id in [k.id for k in team1]:
                            footer_text = f"🔴 {u.name}, You are already in this Team"
                        elif u.id in [k.id for k in team2]:
                            indexRemove: int
                            for omb in range(len(team2)):
                                if team2[omb].id == u.id:
                                    indexRemove = omb
                            obj = team2[indexRemove]
                            team2.pop(indexRemove)
                            team1.append(obj)
                            footer_text = f"🔴 {u.name} Leave the Blue Team and Joined Red Team"
                        else:
                            obj = checkClassID(u)
                            team1.append(obj)
                            footer_text = f"🔴 {u.name} Joined Red Team"
                else:
                    if len(team2) == max_pcount:
                        footer_text = "Party Already Full"
                    else:
                        if u.id in [k.id for k in team1]:
                            indexRemove: int
                            for omb in range(len(team1)):
                                if team1[omb].id == u.id:
                                    indexRemove = omb
                            obj = team1[indexRemove]
                            team1.pop(indexRemove)
                            team2.append(obj)
                            footer_text = f"🔵 {u.name} Leave the Red Team and Joined Blue Team"
                        elif u.id in [k.id for k in team2]:
                            footer_text = f"🔵 {u.name}, You are already in this Team"
                        else:
                            obj = checkClassID(u)
                            team2.append(obj)
                            footer_text = f"🔵 {u.name} Joined Blue Team"
                await r.remove(u)
                if len(team1) == max_pcount and len(team2) == max_pcount:
                    break

                # Edit Hint Message
                emb = discord.Embed(
                    title= "⌛ Waiting for Other Player to Join...",
                    description= f"{max_pcount}v{max_pcount} mode",
                    colour= WHITE
                    )
                emb.add_field(
                    name= "🔴 Red Team",
                    value= "\n".join([f"> **{j.name}** ({j.ClassName})" for j in team1]) if len(team1) > 0 else "```Empty Room```",
                    inline= False
                    )
                emb.add_field(
                    name= "🔵 Blue Team",
                    value= "\n".join([f"> **{j.name}** ({j.ClassName})" for j in team2]) if len(team2) > 0 else "```Empty Room```",
                    inline= False
                    )
                emb.set_footer(text= footer_text)
                await hm.edit(embed= emb)

            # After it has been fulfiled, then let's Begin!
            await hm.delete()
            await self._lets_battle(context, team1, team2)
        except asyncio.TimeoutError:
            await hm.delete(delay= 1)
            await channel.send("*⚔️ Battle Canceled, Queue Timeout*")
            await self._cooling_down(channel.id)

    # Gameplay

    async def _lets_battle(self, ctx: commands.Context, t1: list, t2: list):
        # Inner Functions
        def find_target(arg):
            if is_number(arg):
                if char_turn[1] == 1:
                    return t2[int(arg) - 1][0]
                else:
                    return t1[int(arg) - 1][0]
            else:
                for char_in in turns:
                    if arg == char_in[0].name:
                        return char_in[0]

        def make_emb():
            emb = discord.Embed(
                title="⚔️ Arena ⚔️",
                colour=WHITE
                )
            emb.add_field(
                name="🔴 Red Team",
                value="\n".join([f"> {j + 1}. **{t1[j][0].name}** `HP: {t1[j][0].HP}/{t1[j][0].MAX_HP} | MANA: {t1[j][0].MANA}/{t1[j][0].MAX_MANA}`" for j in range(len(t1))]),
                inline=False
                )
            emb.add_field(
                name="🔵 Blue Team",
                value="\n".join([f"> {j + 1}. **{t2[j][0].name}** `HP: {t2[j][0].HP}/{t2[j][0].MAX_HP} | MANA: {t2[j][0].MANA}/{t2[j][0].MAX_MANA}`" for j in range(len(t2))]),
                inline=False
                )
            descr: str = ""
            if get_started is True:
                descr = "```Empty Log```"
            else:
                descr += f"`{char_turn[0].AttMsg}`\n"
                descr += f"`{target.AttMsg}`"
            emb.add_field(
                name="📄 Battle Log",
                value=descr,
                inline=False
                )
            emb.set_author(
                name=f"{turns[index][0].person.name}, Your Turn!",
                icon_url=turns[index][0].person.avatar_url
                )
            emb.set_footer(text="Send move Message in this channel.")
            return emb

        def check_reply(user: discord.User):
            def inner_check(message: discord.Message):
                argument: list or tuple = message.content.split(' ')
                names_in_game: list = [ch[0].name for ch in turns]
                if argument[0].lower() == "use" and len(argument) == 3 and message.author == user:
                    if argument[1].lower() == "normal":
                        if is_number(argument[2]):
                            if int(argument[2]) <= len(turns) and int(argument[2]) > 0:
                                return True
                        elif argument[2] in names_in_game:
                            return True
                    # elif is_number(argument[1]):
                    #     if int(argument[1]) < len(moves) and (is_number(argument[2]) or argument[2] in names_in_game):
                    #         return True
                    # elif (argument[1] in moves or argument[1] in items) and (is_number(argument[2]) or argument[2] in names_in_game):
                    #     return True
                return False
            return inner_check

        # Initialize Attribute
        get_started: bool = True
        turns: list = []
        send_count: int = 0
        index: int = 0
        async with ctx.typing():
            # Initialize Turn
            for i in t1:
                while index < len(turns):
                    if i.SPD > turns[index][0].SPD:
                        break
                    index += 1
                turns.insert(index, (i, 1))
                index = 0
            for j in t2:
                while index < len(turns):
                    if j.SPD > turns[index][0].SPD:
                        break
                    index += 1
                turns.insert(index, (j, 2))
                index = 0

            # Send Hint to all PPL and Channel
            for k in turns:
                await k[0].person.send(embed=k[0].GetHint)
            t1 = [(turns[c1][0], c1, 1) for c1 in range(len(turns)) if turns[c1][1] == 1]
            t2 = [(turns[c2][0], c2, 2) for c2 in range(len(turns)) if turns[c2][1] == 2]
            hm: discord.Message = await ctx.send(embed=make_emb())

        # Game ON!
        survivet1: int; survivet2: int; 
        char_turn = None; target = None
        try:
            while True:
                # Player Send Move to opposition
                char_turn = turns[index]
                reply: discord.Message = await self.bot.wait_for(
                    event="message",
                    check=check_reply(char_turn[0].person),
                    timeout=60.0
                    )
                
                # Check Use
                reply_cont: list = reply.content.split(' ')
                await reply.delete()
                target = find_target(reply_cont[2])
                if reply_cont[1].lower() == 'normal':
                    if target.id == char_turn[0].id:
                        continue
                    # Attack and Defend
                    att_type, rawdmg = char_turn[0].NormalAttack()
                    target.Defend(att_type, rawdmg)
                    
                # elif is_number(reply_cont[1]):
                #     print("use Move")

                # elif reply_cont[1] in char_turn.Moves:
                #     print("use Move")

                # elif reply_cont[1] in char_turn.Items:
                #     print("use item")
                
                else:
                    continue

                async with ctx.typing():
                    # Check Team Completion
                    survivet1 = 0; survivet2 = 0
                    for pt1 in t1:
                        if pt1[0].HP > 0:
                            survivet1 += 1
                    for pt2 in t2:
                        if pt2[0].HP > 0:
                            survivet2 += 1
                    if survivet1 == 0 or survivet2 == 0:
                        break

                    # Edit Hint, Resend Battle Message
                    get_started = False
                    index = (index+1) if index < len(turns) - 1 else 0
                    send_count = (send_count+1) if send_count < 2 else 0
                    if send_count == 0:
                        await hm.delete()
                        hm = await ctx.send(embed=make_emb())
                    else:
                        await hm.edit(embed=make_emb())

            # Send Reward
            if survivet1 <= 0:
                for i in t2:
                    if i[0].MemberData is not None:
                        if "EXP" in i[0].MemberData:
                            self.mdb.IncreaseItem({"member_id": str(i[0].id)}, {"EXP": RewardEXP})
                            self.gdb.IncreaseItem({"guild_id": str(ctx.guild.id)}, {f"member.{str(i[0].id)}.money": RewardMoney})
            else:
                for i in t1:
                    if i[0].MemberData is not None:
                        if "EXP" in i[0].MemberData:
                            self.mdb.IncreaseItem({"member_id": str(i[0].id)}, {"EXP": RewardEXP})
                            self.gdb.IncreaseItem({"guild_id": str(ctx.guild.id)}, {f"member.{str(i[0].id)}.money": RewardMoney})

        except asyncio.TimeoutError:
            await hm.delete(delay=1)
            await ctx.send(f"*Gameplay turn Timeout! {turns[index][0].name}, where have you been?*")

    # Others

    @staticmethod
    async def print_help(channel: discord.TextChannel):
        pref: str = get_prefix(channel.guild.id)
        emb = discord.Embed(
            title= "⚔️ Battlefield | Help",
            description= f"A Turnbase RPG game, you will pay it manually, don't forget to {pref}.start to start your progress.",
            colour= discord.Colour(WHITE)
            )
        emb.add_field(
            name= "Command :",
            value= f"{pref}.battle <mode>",
            inline= False
            )
        emb.add_field(
            name= "Mode :",
            value= "`1v1` - 1 vs 1 Player\n"
                "`2v2` - 2 vs 2 Player\n"
                "`3v3` - 3 vs 3 Player",
            inline= False
            )
        emb.set_footer(text= f"Example Command : {pref}.battle 1v1")
        await channel.send(embed= emb)
        
def setup(bot: commands.Bot):
    bot.add_cog(Battle(bot))