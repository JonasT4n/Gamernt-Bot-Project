import discord
import asyncio
from discord.ext import commands
from Settings.MyUtility import checkin_member, get_prefix, convert_rpg_substat
from Settings.StaticData import rpg_lvl_data
from Settings.MongoManager import MongoManager

WHITE = 0xfffffe

class Experience(commands.Cog):

    PERLEVEL: int = 50
    DATA_LVL: dict = {}

    def __init__(self, bot: commands.Bot, lvl_init: dict):
        self.bot = bot
        self.mdb = MongoManager(collection= "members")
        for i in lvl_init:
            self.DATA_LVL[i] = {"LVL": {}, "SUM": {}}
            self.DATA_LVL[i]["EFF"] = lvl_init[i]["eff"]
            for j in range(0, 25 + 1):
                if j == 0:
                    self.DATA_LVL[i]["LVL"][j] = 0
                    self.DATA_LVL[i]["SUM"][j] = 0
                elif j == 1:
                    self.DATA_LVL[i]["LVL"][j] = lvl_init[i]["lvl1"]
                    self.DATA_LVL[i]["SUM"][j] = lvl_init[i]["lvl1"]
                else:
                    self.DATA_LVL[i]["LVL"][j] = self.DATA_LVL[i]["LVL"][j - 1] - lvl_init[i]["dec"]
                    self.DATA_LVL[i]["SUM"][j] = self.DATA_LVL[i]["SUM"][j - 1] + self.DATA_LVL[i]["LVL"][j]

    # Event Listener Area

    @commands.Cog.listener()
    async def on_ready(self):
        print("Currency Manager is Ready!")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        mbr_data: dict = checkin_member(message.author.id)
        if message.content.startswith(get_prefix(message.guild.id)):
            return
        if "EXP" in mbr_data:
            if self.PERLEVEL * (mbr_data["LVL"] + 1) <= mbr_data["EXP"] + 1:
                self.mdb.SetObject({"member_id": str(message.author.id)}, {"EXP": 0})
                self.mdb.IncreaseItem({"member_id": str(message.author.id)}, {"LVL": 1, "skill-point": 1})
                emb = discord.Embed(
                    title= "LEVEL UP!",
                    description= f"{message.author.name}, you are now level **{mbr_data['LVL'] + 1}**!",
                    colour= discord.Colour(WHITE)
                    )
                emb.set_thumbnail(url= message.author.avatar_url)
                await message.channel.send(embed= emb)
            else:
                self.mdb.IncreaseItem({"member_id": str(message.author.id)}, {"EXP": 1})

    # Checker Area

    @staticmethod
    def is_number(string: str):
        for word in string:
            if not (48 <= ord(word) < 58):
                return False
        return True

    # Commands Area

    @commands.command(name= "stat", pass_context= True)
    async def _stat(self, ctx: commands.Context, *, person: discord.Member = None):
        if person is None:
            person = ctx.author
        if person.bot is True:
            return
        mbr_data: dict = checkin_member(person.id)
        if "MAX-STAT" in mbr_data:
            lvl: int = mbr_data['LVL']
            stat: dict = convert_rpg_substat(mbr_data["MAX-STAT"], return_value= True)
            emb = discord.Embed(
                title= mbr_data['title'],
                description= f"`CLASS` : {mbr_data['CHAR']}\n"
                    f"`Level` : {lvl} | EXP : {mbr_data['EXP']}/{(lvl + 1) * self.PERLEVEL}\n"
                    f"`Skill Point` : {mbr_data['skill-point']}",
                colour= discord.Colour(WHITE)
                )
            emb.add_field(
                name= "Skill Stat",
                value= f"> `Strength` : {mbr_data['PRIM-STAT']['STR']} / 25\n"
                    f"> `Endurance` : {mbr_data['PRIM-STAT']['END']} / 25\n"
                    f"> `Agility` : {mbr_data['PRIM-STAT']['AGI']} / 25\n"
                    f"> `Focus` : {mbr_data['PRIM-STAT']['FOC']} / 25",
                inline= True
                )
            emb.add_field(
                name= "Substat",
                value= f"> `HP` : {stat['HP']} | `DEF` : {stat['DEF']}\n"
                    f"> `SPD` : {stat['SPD']} | `ATT` : {stat['MIN-ATT']}-{stat['MAX-ATT']}\n"
                    f"> `Critical Chance` : {stat['CRIT']}%",
                inline= True
                )
            emb.set_author(
                name= ctx.author.nick if ctx.author.nick is not None else ctx.author.name,
                icon_url= ctx.author.avatar_url
                )
            await ctx.send(embed= emb)
        else:
            await ctx.send(f"__**You haven't start your character, type {get_prefix(ctx.guild.id)}start to begin.**__")

    @commands.command(name= "skilladd", pass_context= True)
    async def _skill_add(self, ctx: commands.Context, *args):
        mbr_data: dict = checkin_member(ctx.author.id)
        if "PRIM-STAT" in mbr_data:
            if len(args) == 0:
                await self.print_skill_add_help(ctx.channel)
            else:
                amount: int = 1
                get_skill: str = ""
                which: str = ""

                if args[0].lower() == "str" or args[0].lower() == "strength":
                    which = "Strength"
                    get_skill = "STR"
                elif args[0].lower() == "end" or args[0].lower() == "endurance":
                    which = "Endurance"
                    get_skill = "END"
                elif args[0].lower() == "agi" or args[0].lower() == "agility":
                    which = "Agility"
                    get_skill = "AGI"
                elif args[0].lower() == "foc" or args[0].lower() == "focus":
                    which = "Focus"
                    get_skill = "FOC"
                else:
                    return

                skill_lvl: int = mbr_data["PRIM-STAT"][get_skill]
                eff_skill: str = self.DATA_LVL[get_skill]["EFF"]
                if len(args) >= 2:
                    if self.is_number(args[1]) is True:
                        amount = int(args[1])

                if mbr_data["skill-point"] < amount:
                    emb = discord.Embed(
                        title= "Not Enough Skillpoint",
                        description= f"You currently have {mbr_data['skill-point']} and it is not enough.",
                        colour= discord.Colour(WHITE)
                        )
                    await ctx.send(embed= emb)
                elif skill_lvl + amount > 25:
                    emb = discord.Embed(
                        title= "Skill Max Exceeded",
                        description= f"You can't upgrade your {which} to {skill_lvl} / 25",
                        colour= discord.Colour(WHITE)
                        )
                    await ctx.send(embed= emb)
                else:
                    self.mdb.IncreaseItem({"member_id": mbr_data["member_id"]}, {
                        "skill-point": -amount,
                        f"PRIM-STAT.{get_skill}": amount,
                        f"MAX-STAT.{eff_skill}": self.DATA_LVL[get_skill]['SUM'][skill_lvl + amount] - self.DATA_LVL[get_skill]['SUM'][skill_lvl]
                        })
                    emb = discord.Embed(
                        title= f"You have upgraded your {which} to {skill_lvl + amount} / 25",
                        colour= discord.Colour(WHITE)
                        )
                    await ctx.send(embed= emb)
        else:
            await ctx.send(f"__**You haven't start your character, type {get_prefix(ctx.guild.id)}start to begin.**__")

    @commands.command(name= "skillreset", aliases= ["skillres"], pass_context= True)
    async def _reset_skill(self, ctx: commands.Context):
        mbr_data: dict = checkin_member(ctx.author.id)
        if "PRIM-STAT" in mbr_data:
            emb = discord.Embed(
                title= "Reset your Skills?",
                description= "Are you sure you want to reset your skills?\n"
                    "> It will reset all your primary stat like Strength, Endurance, and etc to Zero. However it will refund all your skillpoint.",
                colour= discord.Colour(WHITE)
                )
            emb.set_footer(text= "React ✅ to continue or ❌ to abort")
            hm: discord.Message = await ctx.send(embed= emb)
            await hm.add_reaction("✅")
            await hm.add_reaction("❌")
            try:
                r: discord.Reaction
                u: discord.User
                r, u = await self.bot.wait_for(
                    event= "reaction_add",
                    check= lambda reaction, user: True if (str(reaction.emoji) == "❌" or str(reaction.emoji) == "✅") and user == ctx.author else False,
                    timeout= 30.0
                    )
                await hm.delete()
                if str(r.emoji) == "✅":
                    hm = await ctx.send("*Resetting your Stat, Wait for a moment.*")
                    skill_set: int = 0
                    for skill in mbr_data["PRIM-STAT"]:
                        temp_amo: int = mbr_data['PRIM-STAT'][skill]
                        skill_set += temp_amo
                        self.mdb.IncreaseItem({"member_id": mbr_data['member_id']}, {f'MAX-STAT.{self.DATA_LVL[skill]["EFF"]}': -self.DATA_LVL[skill]["SUM"][temp_amo]})
                        self.mdb.SetObject({"member_id": mbr_data['member_id']}, {f'PRIM-STAT.{skill}': 0})
                    self.mdb.IncreaseItem({"member_id": mbr_data['member_id']}, {"skill-point": skill_set})
                    await hm.delete()
                    await ctx.send(embed= discord.Embed(title= f"{ctx.author.name} has reset his/her Skills. Refunded {skill_set} Skillpoint(s)", colour= discord.Colour(WHITE)))
                else:
                    await ctx.send("*Aborted*")
            except asyncio.TimeoutError:
                await hm.delete()
                await ctx.send("*Request Timeout*")
        else:
            await ctx.send(f"__**You haven't start your character, type {get_prefix(ctx.guild.id)}start to begin.**__")

    # Others

    @staticmethod
    async def print_skill_add_help(channel: discord.TextChannel):
        pref: str = get_prefix(channel.guild.id)
        emb = discord.Embed(
            title= "Add Skill | Help",
            description= "Use your Skillpoint to increase your primary stat.\n"
                "These are the skill you can increase it : `Strength` `Endurance` `Agility` `Focus`",
            colour= discord.Colour(WHITE)
            )
        emb.add_field(
            name= "Command : ",
            value= f"`{pref}skilladd <skill> <amount>`",
            inline= False
            )
        emb.set_footer(text= f"Example Command to Upgrade Strength : {get_prefix(channel.guild.id)}skilladd strength 3")
        await channel.send(embed= emb)

def setup(bot: commands.Bot):
    bot.add_cog(Experience(bot, rpg_lvl_data))