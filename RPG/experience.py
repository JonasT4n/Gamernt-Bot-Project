import discord
import asyncio
import requests
import PIL
import os
import random
from PIL import Image, ImageDraw, ImageOps, ImageFont
from discord.ext import commands
from Settings.MyUtility import checkin_member, checkin_guild, get_prefix, is_number, db_mbr, add_exp, checkClassID
from RPGPackage.RPGAttribute import *

WHITE = 0xfffffe

class Experience(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Event Listener Area
    # On Message Event, including adding experiences when chatting in server.
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore DM Channel
        if isinstance(message.channel, discord.DMChannel):
            return
        
        gld_data = checkin_guild(message.guild)
        if gld_data["event-channel"] is not None:
            channel: discord.TextChannel = self.bot.get_channel(int(gld_data["event-channel"]))
            await add_exp(channel, message.author, 1)
        else:
            await add_exp(message.channel, message.author, 1)

    # Commands Area

    @commands.command(name="stat",)
    async def _stat(self, ctx: commands.Context, *, person: discord.Member = None):
        person = ctx.author if person is None else person
        mbr_data = checkin_member(person)
        if mbr_data is not None:
            if "PRIM-STAT" in mbr_data:
                async with ctx.typing():
                    image_name: str = self.generate_stat_image(person, mbr_data)
                    stat: Player = checkClassID(person)
                    emb = discord.Embed(
                        title=mbr_data['title'],
                        description=f"`CLASS` : {stat.ClassName}\n",
                        colour=WHITE
                        )
                    emb.add_field(
                        name= "Skill Stat",
                        value= f"`Strength` : {mbr_data['PRIM-STAT']['STR']} / {MAXSKILL}\n"
                            f"`Endurance` : {mbr_data['PRIM-STAT']['END']} / {MAXSKILL}\n"
                            f"`Agility` : {mbr_data['PRIM-STAT']['AGI']} / {MAXSKILL}\n"
                            f"`Focus` : {mbr_data['PRIM-STAT']['FOC']} / {MAXSKILL}\n"
                            f"`Intelligence` : {mbr_data['PRIM-STAT']['ITE']} / {MAXSKILL}\n"
                            f"`Wise` : {mbr_data['PRIM-STAT']['WIS']} / {MAXSKILL}",
                        inline= True
                        )
                    emb.add_field(
                        name= "Substat",
                        value= f"`HP`: {stat.HP} | `Mana`: {stat.MANA}\n"
                            f"`DEF`: {stat.DEF} | `Magic DEF`: {stat.MDEF}\n"
                            f"`ATT`: {stat.ATT} | `Magic ATT`: {stat.MATT}\n"
                            f"`SPD`: {stat.SPD}\n"
                            f"`Critical Chance`: {stat.CRIT}%",
                        inline= True
                        )
                    emb.set_author(
                        name=person.nick if person.nick is not None else person.name,
                        icon_url=person.avatar_url
                        )
                with open(f"./{image_name}", 'rb') as f:
                    await ctx.send(embed=emb, file=discord.File(f, filename=image_name))
                    f.close()
                if os.path.exists(image_name):
                    os.remove(image_name)
            else:
                await ctx.send(f"__**{person.name}, You haven't start your character, type {get_prefix(ctx.guild.id)}start to begin.**__")

    @commands.command(name="skilladd", aliases=["addskill"])
    async def _skill_add(self, ctx: commands.Context, *args):
        mbr_data: dict = checkin_member(ctx.author)
        if mbr_data is not None:
            if "PRIM-STAT" in mbr_data:
                if len(args) == 0:
                    await self.print_skill_add_help(ctx.channel)
                else:
                    amount: int = 1 # Skill Amount
                    get_skill: str = ""
                    which: str = ""

                    # Choose Ability
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
                    elif args[0].lower() == "ite" or args[0].lower() == "intelligence":
                        which = "Intelligence"
                        get_skill = "ITE"
                    elif args[0].lower() == "wis" or args[0].lower() == "wise":
                        which = "Wise"
                        get_skill = "WIS"
                    else:
                        return

                    skill_lvl: int = mbr_data["PRIM-STAT"][get_skill]
                    if len(args) >= 2:
                        if is_number(args[1]) is True:
                            amount = int(args[1])

                    # Check if Able to Upgrade
                    if mbr_data["skill-point"] < amount:
                        emb = discord.Embed(
                            title="Not Enough Skillpoint",
                            description=f"You currently have {mbr_data['skill-point']} and it is not enough.",
                            colour=WHITE
                            )
                        await ctx.send(embed=emb)
                    elif skill_lvl + amount > MAXSKILL:
                        emb = discord.Embed(
                            title="Skill Max Exceeded",
                            description=f"You can't upgrade your {which} to {skill_lvl} / {MAXSKILL}",
                            colour=WHITE
                            )
                        await ctx.send(embed=emb)

                    # Upgrade Skill
                    else:
                        db_mbr.IncreaseItem({"member_id": mbr_data["member_id"]}, {"skill-point": -amount, f"PRIM-STAT.{get_skill}": amount,})
                        emb = discord.Embed(
                            title=f"You have upgraded your {which} to {skill_lvl + amount} / {MAXSKILL}",
                            colour=WHITE
                            )
                        await ctx.send(embed=emb)
            else:
                await ctx.send(f"__**{ctx.author.name}, You haven't start your character, type {get_prefix(ctx.guild.id)}start to begin.**__")

    @commands.command(name="skillreset", aliases=["skillres", "resetskill"])
    async def _reset_skill(self, ctx: commands.Context):
        mbr_data: dict = checkin_member(ctx.author)
        if mbr_data is not None:
            if "PRIM-STAT" in mbr_data:
                # Send Hint
                menus: list = ["✅", "❌"]
                emb = discord.Embed(
                    title="Reset your Skills?",
                    description="Are you sure you want to reset your skills?\n"
                            "> It will reset all your primary stat like Strength, Endurance, and etc to Zero. However it will refund all your skillpoint.",
                    colour=WHITE
                    )
                emb.set_footer(text="React ✅ to continue or ❌ to abort")
                hm: discord.Message = await ctx.send(embed=emb)
                for i in menus:
                    await hm.add_reaction(i)

                try:
                    # Waiting for Response
                    r: discord.Reaction
                    u: discord.User
                    r, u = await self.bot.wait_for(
                        event="reaction_add",
                        check=lambda reaction, user: True if str(reaction.emoji) in menus and user == ctx.author else False,
                        timeout=30.0
                        )
                    await hm.delete()

                    # Proceed
                    if str(r.emoji) == "✅":
                        hm = await ctx.send("*Resetting your Stat, Wait for a moment.*")
                        skill_set: int = 0
                        for skill in mbr_data["PRIM-STAT"]:
                            temp_amo: int = mbr_data['PRIM-STAT'][skill]
                            skill_set += temp_amo
                            db_mbr.SetObject({"member_id": mbr_data['member_id']}, {f'PRIM-STAT.{skill}': 0})
                        db_mbr.SetObject({"member_id": mbr_data['member_id']}, {"skill-point": mbr_data['LVL']})
                        await hm.delete()
                        await ctx.send(embed=discord.Embed(
                                    title= f"{ctx.author.name} has reset his/her Skills. Refunded {skill_set} Skillpoint(s)", 
                                    colour=WHITE))

                    # Abort
                    else:
                        await ctx.send("*Aborted*")

                except asyncio.TimeoutError:
                    await hm.delete()
                    await ctx.send("*Request Timeout*")
            else:
                await ctx.send(f"__**{ctx.author.name}, You haven't start your character, type {get_prefix(ctx.guild.id)}start to begin.**__")

    # Generate Image

    def generate_stat_image(self, person: discord.User, data: dict) -> str:
        # Attribute
        exp: int = data["EXP"]
        lvl: int = data["LVL"]
        max_value = (lvl+1) * PERLEVEL if lvl < MAXLEVEL else 1
        description: str = f"LVL {lvl if lvl != MAXLEVEL else f'MAX'}   |   EXP : {exp}/{max_value}   |   SP : {data['skill-point']}"

        stat_size = (640, 120)
        min_point = (135, 65)
        max_point = (560, 90)

        # Download Temporary Image
        url = person.avatar_url
        img_data = requests.get(url).content
        with open("./rawImgPerson.jpg", "wb") as h:
            h.write(img_data)
            h.close()

        # Init
        level_bar = Image.open("./Asset/barbgn.jpg")
        pfp = Image.open("./rawImgPerson.jpg")
        mask = Image.open("./Asset/pfpmask.png")
        font = ImageFont.truetype("./Asset/EvilEmpire-4BBVK.ttf", 32)

        # Make Image
        draw = ImageDraw.Draw(level_bar)
        draw.rectangle([(60, 10), (620, 110)], fill= (0, 0, 0, 100))
        draw.text((135, 20), text= description, fill= 'white', font= font)

        length_progress = (exp / max_value) * (max_point[0] - min_point[0]) + min_point[0]
        draw.rectangle([min_point, (length_progress, max_point[1])], fill= 'white')
        draw.rectangle([min_point, max_point], outline= (255, 255, 255), width= 2)

        pfp = ImageOps.fit(pfp, mask.size)
        level_bar.paste(pfp, (10, 10), mask= mask)
        draw.ellipse([(10, 10), (110, 110)], outline= 'white', width= 2)

        # Save File
        imgid: str = self._generate_id()
        level_bar.save(f"{imgid}.jpg")

        # Delete Temporary Image
        if os.path.exists(f"./rawImgPerson.jpg"):
            os.remove(f"./rawImgPerson.jpg")
        return imgid + ".jpg"

    # Others

    @staticmethod
    def _generate_id() -> str:
        ids: str = "B"
        while len(ids) < 9:
            ids += random.choice([
                chr(random.randint(48, 57)), 
                chr(random.randint(65, 90)), 
                chr(random.randint(97, 122))
                ])
        return ids

    @staticmethod
    async def print_skill_add_help(channel: discord.TextChannel):
        pref: str = get_prefix(channel.guild)
        emb = discord.Embed(
            title="Add Skill | Help",
            description="Use your Skillpoint to increase your primary stat.\n"
                    "These are the skill you can increase it : `Strength` `Endurance` `Agility` `Focus` `Intelligence` `Wise`",
            colour=WHITE
            )
        emb.add_field(
            name="Command : ",
            value=f"`{pref}skilladd <skill> <amount>`",
            inline=False
            )
        emb.set_footer(text=f"Example Command to Upgrade Strength : {get_prefix(channel.guild.id)}skilladd strength 3")
        await channel.send(embed=emb)

def setup(bot: commands.Bot):
    bot.add_cog(Experience(bot))