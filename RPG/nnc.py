import discord
from discord.ext import commands
from Settings.MyUtility import get_prefix, checkin_member
from Settings.MongoManager import MongoManager

WHITE = 0xfffffe

class NNC(commands.Cog):

    CLASSES: dict = {
            1: "Warrior",
            2: "Mage"
        }
    NATURES: dict = {
            1: "Normal",
            2: "Aggresive"
        }

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.mdb = MongoManager(collection= "members")

    # Checker Area

    @staticmethod
    def is_number(string: str):
        for word in string:
            if not (48 <= ord(word) < 58):
                return False
        return True

    # Commands

    @commands.command(name= "class", pass_context= True)
    async def _rpg_class(self, ctx: commands.Context, *args):
        mbr_data: dict = checkin_member(ctx.author.id)
        if "CLASSID" in mbr_data:
            if len(args) == 0:
                await self._class_help(ctx.channel)
            else:
                # Get Info
                if args[0].lower() == "info" or args[0].lower() == "-i":
                    pass
                
                # Change Class
                elif self.is_number(args[0]):
                    if args[0] > len(self.CLASSES) or args[0] <= 0:
                        return
                    else:
                        if mbr_data['CLASSID'] == args[0]:
                            await ctx.send(content= f"*You are already in class {self.CLASSES[args[0]]}*")
                        else:
                            self.mdb.SetObject({"member_id": str(ctx.author.id)}, {'CLASSID': args[0]})
                            await ctx.send(content= f"*You have changed from {self.CLASSES[mbr_data['CLASSID']]} to {self.CLASSES[args[0]]}.*")

                else:
                    pass
        else:
            await ctx.send(f"__**{ctx.author.name}, You haven't start your character, type {get_prefix(ctx.guild.id)}start to begin.**__")

    @commands.command(name= "nature", pass_context= True)
    async def _rpg_nature(self, ctx: commands.Context, *args):
        mbr_data: dict = checkin_member(ctx.author.id)
        if "CHARID" in mbr_data:
            if len(args) == 0:
                await self._nature_help(ctx.channel)
            else:
                # Get Info
                if args[0].lower() == "info" or args[0].lower() == "-i":
                    pass
                
                # Change Nature
                elif self.is_number(args[0]):
                    if args[0] > len(self.NATURES) or args[0] <= 0:
                        return
                    else:
                        if mbr_data['CHARID'] == args[0]:
                            await ctx.send(content= f"*You are already in class {self.NATURES[args[0]]}*")
                        else:
                            self.mdb.SetObject({"member_id": str(ctx.author.id)}, {'CHARID': args[0]})
                            await ctx.send(content= f"*You have changed from {self.NATURES[mbr_data['CHARID']]} to {self.NATURES[args[0]]}.*")

                else:
                    pass
        else:
            await ctx.send(f"__**{ctx.author.name}, You haven't start your character, type {get_prefix(ctx.guild.id)}start to begin.**__")

    # Others

    @staticmethod
    async def _class_help(channel: discord.TextChannel):
        pref: str = get_prefix(channel.guild.id)
        emb = discord.Embed(
            title= " Classes | List",
            description= "Change your class, you can be :\n"
                "> 1. `Warrior`\n"
                "> 2. `Mage`\n",
            colour= discord.Colour(WHITE)
            )
        emb.add_field(
            name= "Command :",
            value= f"> `{pref}class <option>`",
            inline= False
            )
        emb.add_field(
            name= "Options :",
            value= "`<number>` - Change your class\n"
                "`-i`|`info` - See class detail",
            inline= False
            )
        emb.set_footer(text= f"Example Command to change your class to Mage : {pref}class 2")
        await channel.send(embed= emb)

    @staticmethod
    async def _nature_help(channel: discord.TextChannel):
        pref: str = get_prefix(channel.guild.id)
        emb = discord.Embed(
            title= " Character Natures | List",
            description= "Change your current nature, your character attitude gonna be :\n"
                "> 1. `Normal`\n"
                "> 2. `Aggresive`\n",
            colour= discord.Colour(WHITE)
            )
        emb.add_field(
            name= "Command :",
            value= f"> `{pref}nature <option>`",
            inline= False
            )
        emb.add_field(
            name= "Options :",
            value= "`<number>` - Change your nature\n"
                "`-i`|`info` - See nature detail",
            inline= False
            )
        emb.set_footer(text= f"Example Command to change your nature to Aggresive : {pref}nature 2")
        await channel.send(embed= emb)

def setup(bot: commands.Bot):
    bot.add_cog(NNC(bot))