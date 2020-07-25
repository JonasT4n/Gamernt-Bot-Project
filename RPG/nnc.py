import discord
from discord.ext import commands
from Settings.MyUtility import get_prefix, checkin_member, db_mbr, is_number
from RPGPackage.RPGCharacter import CLASSES, NATURES

WHITE = 0xfffffe

class NNC(commands.Cog):

    # Cog Constructor
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Commands Area
    # Change Character Class Command
    @commands.command(name="class")
    async def _rpg_class(self, ctx: commands.Context, *args):
        mbr_data = checkin_member(ctx.author)
        if mbr_data is not None:
            if "CLASSID" in mbr_data:
                if len(args) == 0:
                    await self._class_help(ctx.channel)
                else:
                    # Get Info
                    if args[0].lower() == "info" or args[0].lower() == "-i":
                        pass
                    
                    # Change Class
                    elif is_number(args[0]):
                        if int(args[0]) > len(self.CLASSES) or int(args[0]) <= 0:
                            return
                        else:
                            if mbr_data['CLASSID'] == int(args[0]):
                                await ctx.send(content= f"*You are already in class {self.CLASSES[int(args[0])]}*")
                            else:
                                db_mbr.SetObject({"member_id": str(ctx.author.id)}, {'CLASSID': int(args[0])})
                                await ctx.send(content= f"*You have changed from {self.CLASSES[mbr_data['CLASSID']]} to {self.CLASSES[int(args[0])]}.*")
            else:
                await ctx.send(f"__**{ctx.author.name}, You haven't start your character, type {get_prefix(ctx.guild)}start to begin.**__")

    # Change Character Nature Command
    @commands.command(name="nature")
    async def _rpg_nature(self, ctx: commands.Context, *args):
        mbr_data = checkin_member(ctx.author)
        if mbr_data is not None:
            if "CHARID" in mbr_data:
                if len(args) == 0:
                    await self._nature_help(ctx.channel)
                else:
                    # Get Info
                    if args[0].lower() == "info" or args[0].lower() == "-i":
                        pass
                    
                    # Change Nature
                    elif is_number(args[0]):
                        if int(args[0]) > len(self.NATURES) or int(args[0]) <= 0:
                            return
                        else:
                            if mbr_data['CHARID'] == int(args[0]):
                                await ctx.send(content= f"*You are already in class {self.NATURES[int(args[0])]}*")
                            else:
                                db_mbr.SetObject({"member_id": str(ctx.author.id)}, {'CHARID': int(args[0])})
                                await ctx.send(content= f"*You have changed from {self.NATURES[mbr_data['CHARID']]} to {self.NATURES[int(args[0])]}.*")
            else:
                await ctx.send(f"__**{ctx.author.name}, You haven't start your character, type {get_prefix(ctx.guild)}start to begin.**__")

    @staticmethod
    async def _class_help(channel: discord.TextChannel):
        pref: str = get_prefix(channel.guild)
        emb = discord.Embed(
            title="🏫 Classes | List",
            description="Change your class, you can be :\n"
                "> 1. `Warrior`\n"
                "> 2. `Mage`\n",
            colour=WHITE
            )
        emb.add_field(
            name="Command :",
            value=f"> `{pref}class <option>`",
            inline=False
            )
        emb.add_field(
            name="Options :",
            value="`<number>` - Change your class\n"
                "`-i`|`info` - See class detail",
            inline=False
            )
        emb.set_footer(text=f"Example Command to change your class to Mage : {pref}class 2")
        await channel.send(embed=emb)

    @staticmethod
    async def _nature_help(channel: discord.TextChannel):
        pref: str = get_prefix(channel.guild)
        emb = discord.Embed(
            title=" Character Natures | List",
            description="Change your current nature, your character attitude gonna be :\n"
                "> 1. `Normal`\n"
                "> 2. `Aggresive`\n",
            colour=WHITE
            )
        emb.add_field(
            name="Command :",
            value=f"> `{pref}nature <option>`",
            inline=False
            )
        emb.add_field(
            name="Options :",
            value="`<number>` - Change your nature\n"
                "`-i`|`info` - See nature detail",
            inline=False
            )
        emb.set_footer(text=f"Example Command to change your nature to Aggresive : {pref}nature 2")
        await channel.send(embed=emb)

def setup(bot: commands.Bot):
    bot.add_cog(NNC(bot))