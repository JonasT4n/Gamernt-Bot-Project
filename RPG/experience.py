import discord
from discord.ext import commands
from Settings.MyUtility import checkin_member, get_prefix, convert_rpg_substat
from Settings.MongoManager import MongoManager

WHITE = 0xfffffe

class Experience(commands.Cog):

    PERLEVEL: int = 50

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.mdb = MongoManager(collection= "members")

    # Event Listener Area

    @commands.Cog.listener()
    async def on_ready(self):
        print("Currency Manager is Ready!")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        mbr_data: dict = checkin_member(message.author.id)
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
                description= f"`CLASS` : {mbr_data['CHAR']}",
                colour= discord.Colour(WHITE)
                )
            emb.add_field(
                name= f"Level {lvl}",
                value= f"> `EXP` : {mbr_data['EXP']}/{(lvl + 1) * self.PERLEVEL} | `Skill Point` : {mbr_data['skill-point']}",
                inline= False
                )
            emb.add_field(
                name= "Skill Stat",
                value= f"> `Strength` : {mbr_data['PRIM-STAT']['STR']}\n"
                    f"> `Endurance` : {mbr_data['PRIM-STAT']['END']}\n"
                    f"> `Agility` : {mbr_data['PRIM-STAT']['AGI']}\n"
                    f"> `Focus` : {mbr_data['PRIM-STAT']['FOC']}",
                inline= False
                )
            emb.add_field(
                name= "Substat",
                value= f"> `HP` : {stat['HP']} | `DEF` : {stat['DEF']}\n"
                    f"> `SPD` : {stat['SPD']} | `ATT` : {stat['MIN-ATT']}-{stat['MAX-ATT']}\n"
                    f"> `Critical Chance` : {stat['CRIT']}%",
                inline= False
                )
            emb.set_author(
                name= ctx.author.nick if ctx.author.nick is not None else ctx.author.name,
                icon_url= ctx.author.avatar_url
                )
            await ctx.send(embed= emb)
        else:
            await ctx.send(f"__**You haven't start your character, type {get_prefix(ctx.guild.id)}start to begin.**__")

def setup(bot: commands.Bot):
    bot.add_cog(Experience(bot))