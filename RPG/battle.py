import discord
import math
import random
import asyncio
from discord.ext import commands, tasks
from Settings.MyUtility import checkin_member, checkin_guild, get_prefix, is_number, add_exp, add_money, checkClassID, send_batte_hint
from RPGPackage.RPGAttribute import *
from RPGPackage.RPGMovement import Movement
from RPGPackage.RPGCharacter import Character

WHITE = 0xfffffe
RewardMoney: int = 2000
RewardEXP: int = 50

class Battle(commands.Cog):

    # Cog Constructor
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Cooler Down
    cooldown: list = []

    async def _cooling_down(self, ids: int):
        self.cooldown.remove(ids)

    @tasks.loop(minutes=3)
    async def _clear_cooldown(self):
        if len(self.cooldown) == 0:
            return
        self.cooldown.clear()

    # Event Listener Area

    @commands.Cog.listener()
    async def on_ready(self):
        self._clear_cooldown.start()

    @commands.Cog.listener()
    async def on_disconnect(self):
        self._clear_cooldown.cancel()

    # Command Area

    @commands.command(name="battle", aliases=['btl'])
    async def _battle(self, ctx: commands.Context, *args):
        mbr_data = checkin_member(ctx.author)
        if mbr_data is not None:
            if "PRIM-STAT" in mbr_data:
                if len(args) == 0:
                    await self.print_help(ctx.channel)
                else:
                    if ctx.channel.id in self.cooldown:
                        hm: discord.Message = await ctx.send(f"*Battle in Progress in this Channel. ({ctx.channel.name})*")
                        await asyncio.sleep(3)
                        await hm.delete()
                        await ctx.message.delete()
                    else:
                        self.cooldown.append(ctx.channel.id)

                        # 1 vs 1 Battle
                        if args[0].lower() == "1v1":
                            await self._queue(ctx.channel, 2)

                        # 2 vs 2 Battle
                        elif args[0].lower() == "2v2":
                            await self._queue(ctx.channel, 4)

                        # 3 vs 3 Battle
                        elif args[0].lower() == "3v3":
                            await self._queue(ctx.channel, 6)
            else:
                await ctx.send(f"__**{ctx.author.name}, You haven't start your character, type {get_prefix(ctx.guild.id)}start to begin.**__")

    # Queue

    async def _queue(self, channel: discord.TextChannel, player_count: int):
        # Send Hint
        teams: list = ["🔴", "🔵"]
        async with channel.typing():
            team1, team2 = [], []
            max_pcount: int = player_count // 2
            emb = discord.Embed(title="⌛ Waiting for Other Player to Join...",
                description=f"{max_pcount}v{max_pcount} mode",
                colour=WHITE)
            emb.add_field(name="🔴 Red Team",
                value="```Empty Room```",
                inline=False)
            emb.add_field(name="🔵 Blue Team",
                value="```Empty Room```",
                inline=False)
            emb.set_footer(text="React to Join One of the Team 🔴 🔵")
        hm: discord.Message = await channel.send(embed=emb)
        for i in teams:
            await hm.add_reaction(i)

        # Edit Hint and Wait for User process
        try:
            while True:
                # Wait for Reaction Reply
                r, u = await self.bot.wait_for(event="reaction_add", timeout=60.0, 
                    check=lambda reaction, user: True if str(reaction.emoji) in teams and user.bot is False else False)

                # Check if user has already registered
                mbr_data = checkin_member(u)
                if mbr_data is not None:
                    if "PRIM-STAT" in mbr_data:
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
                    else:
                        footer_text = f"{u.name} hasn't registered yet, type `{get_prefix(channel.guild)}start` to begin with RPG"

                    # Edit Hint Message
                    async with channel.typing():
                        emb = discord.Embed(title="⌛ Waiting for Other Player to Join...",
                            description=f"{max_pcount}v{max_pcount} mode", colour=WHITE)
                        emb.add_field(name="🔴 Red Team", inline=False, 
                            value="\n".join([f"> **{j.name}** ({j.ClassName})" for j in team1]) if len(team1) > 0 else "```Empty Room```")
                        emb.add_field(name="🔵 Blue Team", inline=False,
                            value="\n".join([f"> **{j.name}** ({j.ClassName})" for j in team2]) if len(team2) > 0 else "```Empty Room```")
                        emb.set_footer(text=footer_text)
                    await hm.edit(embed=emb)

            # After it has been fulfiled, then let's Begin!
            await hm.delete()
            await self._lets_battle(channel, team1, team2)
        except asyncio.TimeoutError:
            await hm.delete(delay=1)
            await channel.send("*⚔️ Battle Canceled, Queue Timeout*")
            await self._cooling_down(channel.id)

    # Gameplay

    async def _lets_battle(self, channel: discord.TextChannel, t1: list, t2: list):
        # Inner Functions
        # it Returns target attack, for default it will return None if not exist
        # Find Target Attack by Index
        def find_target_by_index(arg: int, target_team: list, *, move_sample: Movement = None, item_sample = None):
            """`team` must contains only `Character` object type."""
            if arg < 1 or arg > len(target_team):
                return None
            
            # Type Move use
            if move_sample is not None:
                # For Single Target, just return the target Character
                if move_sample.GetTargetID() == 1:
                    return target_team[arg - 1]
                
                # For Multiple Target
                else:
                    # Making sure the target is on the first index, then return a list of target
                    copy_team = target_team.copy()
                    list_target = [copy_team[arg - 1]]
                    del copy_team[arg - 1]
                    return list_target + copy_team
                
            return None

        # Find Target Attack by Name
        def find_target_by_name(arg: str, target_team: list, *, move_sample: Movement = None, item_sample = None):
            """`team` must contains only `Character` object type."""
            team_names = [n.name for n in target_team]
            if arg not in team_names:
                return None
            
            # Type Move use
            if move_sample is not None:
                # For Single Target, just return the target Character
                if move_sample.GetTargetID() == 1:
                    return team[team_names.index(arg)]
                
                # For Multiple Target
                else:
                    # Making sure the target is on the first index, then return a list of target
                    copy_team = target_team.copy()
                    list_target = [copy_team[team_names.index(arg)]]
                    del copy_team[team_names.index(arg)]
                    return list_target + copy_team
                
            return None

        def make_emb():
            nonlocal target
            emb = discord.Embed(title="⚔️ Arena ⚔️", description=f"**{turns[index][0].name}, Your Turn!**", colour=WHITE)
            emb.add_field(name=f"🔴 Red Team | Alive {survivet1}", inline=False, 
                value="\n".join([f"> {j + 1}. **{t1[j][0].name}** `HP: {t1[j][0].HP}/{t1[j][0].MAX_HP} | MANA: {t1[j][0].MANA}/{t1[j][0].MAX_MANA}`" for j in range(len(t1))]))
            emb.add_field(name=f"🔵 Blue Team | Alive {survivet2}", inline=False, 
                value="\n".join([f"> {j + 1}. **{t2[j][0].name}** `HP: {t2[j][0].HP}/{t2[j][0].MAX_HP} | MANA: {t2[j][0].MANA}/{t2[j][0].MAX_MANA}`" for j in range(len(t2))]))
            descr: str = ""
            if get_started is True:
                descr = "```Empty Log```"
            else:
                descr += f"`{char_turn[0].Msg}`\n"
                if isinstance(target, list):
                    for i in target:
                        descr += f"`{i.Msg}`"
                else:
                    descr += f"`{target.Msg}`"
            emb.add_field(name="📄 Battle Log", value=descr, inline=False)
            emb.set_footer(text="Send move Message in this channel.")
            return emb

        # Check user reply usage
        def check_reply(char: Character, your_team: list, opposition_team: list):
            nonlocal target
            def inner_check(message: discord.Message):
                nonlocal target
                argument: list or tuple = message.content.split(' ')
                # 3 Argument beginning with "use" statement
                if argument[0].lower() == "use" and len(argument) == 3 and message.author.id == char.id:
                    # Specify what do player want to do
                    # Using a normal move from Character
                    if argument[1].lower() == "normal":
                        if is_number(argument[2]):
                            target = find_target_by_index(int(argument[2]), opposition_team, move_sample=char._normal_move)
                        else:
                            target = find_target_by_name(argument[2], opposition_team, move_sample=char._normal_move)
                        
                        # Use Character Normal Move
                        if target is not None:
                            char.NormalAttack(target)
                            return True
                        
                    # Using a custom move from Character
                    elif is_number(argument[1]):
                        if int(argument[1]) >= 1 or int(argument[1]) <= len(char._custom_moves):
                            if is_number(argument[2]):
                                target = find_target_by_index(int(argument[2]), opposition_team, move_sample=char._normal_move)
                            else:
                                target = find_target_by_name(argument[2], opposition_team, move_sample=char._normal_move)
                            
                            # Use Character Normal Move
                            if target is not None:
                                char.CustomAttack(target, int(argument[1]))
                                return True
                        
                    # Using a item from Character
                    # elif (argument[1] in moves or argument[1] in items) and (is_number(argument[2]) or argument[2] in names_in_game):
                    #     return True
                return False
            return inner_check

        # Initialize Attribute
        turns: list = []; get_started: bool = True
        send_count, index = 0, 0
        survivet1: int = len(t1); survivet2: int = len(t2)
        char_turn = None; target = None
        
        # Preparing Turns and Teams
        async with channel.typing():
            # For Team 1 (Red Team)
            for i in t1:
                while index < len(turns):
                    if i.SPD > turns[index][0].SPD:
                        break
                    index += 1
                turns.insert(index, (i, 1)) # 1 means the team id for Red Team
                index = 0
                
            # For Team 2 (Blue Team)
            for j in t2:
                while index < len(turns):
                    if j.SPD > turns[index][0].SPD:
                        break
                    index += 1
                turns.insert(index, (j, 2)) # 2 means the team id for Blue Team
                index = 0

            # Send Hint to all PPL and Channel
            for k in turns:
                char_user: discord.User = self.bot.get_user(k[0].id)
                await send_batte_hint(char_user, k[0])
            t1 = [(turns[c1][0], c1) for c1 in range(len(turns)) if turns[c1][1] == 1]
            t2 = [(turns[c2][0], c2) for c2 in range(len(turns)) if turns[c2][1] == 2]
        hm: discord.Message = await channel.send(embed=make_emb())

        # Game ON!
        try:
            while True:
                # Waiting for user to input action
                # Turn Character, then user need to send action
                char_turn = turns[index]
                if char_turn[0].HP == 0:
                    index = (index+1) if index < len(turns) - 1 else 0
                    continue
                    
                # Character from Red Team
                reply: discord.Message = None
                if char_turn[1] == 1:
                    reply = await self.bot.wait_for(event="message", timeout=60.0, check=check_reply(char_turn[0], [i[0] for i in t1], [j[0] for j in t2]))
                # Character from Blue Team
                else:
                    reply = await self.bot.wait_for(event="message", timeout=60.0, check=check_reply(char_turn[0], [i[0] for i in t2], [j[0] for j in t1]))
                await reply.delete()
                
                async with channel.typing():
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
                    hm = await channel.send(embed=make_emb())
                else:
                    await hm.edit(embed=make_emb())

            # Send Reward
            gld_data = checkin_guild(channel.guild)
            event_channel: discord.TextChannel = self.bot.get_channel(int(gld_data["event-channel"])) if gld_data["event-channel"] is not None else channel
            if survivet1 <= 0:
                for i in t2:
                    char_user = self.bot.get_user(i[0].id)
                    await add_exp(event_channel, char_user, RewardEXP)
                    await add_money(channel.guild.id, char_user, RewardMoney)
                for i in t1:
                    char_user = self.bot.get_user(i[0].id)
                    await add_exp(event_channel, char_user, math.ceil(RewardEXP - (RewardEXP * (80/100))))
                    await add_money(channel.guild.id, char_user, math.ceil(RewardMoney - (RewardMoney * (80/100))))
                emb = discord.Embed(title="🔵 Blue Team Wins!", colour=WHITE, 
                    description="\n".join([f"> {winner[0].name}" for winner in t2]),)
                emb.add_field(name="Reward :", inline=False, 
                    value=f"EXP: {RewardEXP} | Money: {RewardMoney} {checkin_guild(channel.guild)['currency']['type']}")
                await channel.send(embed=emb)
            else:
                for i in t1:
                    char_user = self.bot.get_user(i[0].id)
                    await add_exp(event_channel, char_user, RewardEXP)
                    await add_money(channel.guild.id, char_user, RewardMoney)
                for i in t2:
                    char_user = self.bot.get_user(i[0].id)
                    await add_exp(event_channel, char_user, math.ceil(RewardEXP - (RewardEXP * (80/100))))
                    await add_money(channel.guild.id, char_user, math.ceil(RewardMoney - (RewardMoney * (80/100))))
                emb = discord.Embed(title="🔴 Red Team Wins!",
                    description="\n".join([f"> {winner[0].name}" for winner in t1]),
                    colour=WHITE)
                emb.add_field(name="Reward :", inline=False, 
                    value=f"EXP: {RewardEXP} | Money: {RewardMoney} {checkin_guild(channel.guild)['currency']['type']}")
                await channel.send(embed=emb)
            # Delete Cooldown
            await self._cooling_down(channel.channel.id)
        except asyncio.TimeoutError:
            await hm.delete(delay=1)
            await channel.send(f"*Gameplay turn Timeout! {char_turn[0].name}, where have you been?*")
            await self._cooling_down(channel.id)

    # Others

    @staticmethod
    async def print_help(channel: discord.TextChannel):
        pref: str = get_prefix(channel.guild)
        emb = discord.Embed(
            title="⚔️ Battlefield | Help",
            description=f"A Turnbase RPG game, you will pay it manually, don't forget to {pref}.start to start your progress.",
            colour=WHITE
            )
        emb.add_field(
            name="Command :",
            value=f"{pref}.battle <mode>",
            inline=False
            )
        emb.add_field(
            name="Mode :",
            value="`1v1` - 1 vs 1 Player\n"
                "`2v2` - 2 vs 2 Player\n"
                "`3v3` - 3 vs 3 Player",
            inline=False
            )
        emb.set_footer(text=f"Example Command : {pref}.battle 1v1")
        await channel.send(embed=emb)
        
def setup(bot: commands.Bot):
    bot.add_cog(Battle(bot))