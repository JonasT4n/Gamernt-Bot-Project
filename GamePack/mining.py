import discord
import asyncio
import random
from Settings.DbManager import DbManager as dbm
from discord.ext import commands

WHITE = 0xfffffe

class Mine(commands.Cog):

    # List of Ores
    kind_ores = ["Copper", "Lead", "Tin", 
            "Cobalt", "Iron", "Coal", 
            "Silver", "Ruby", "Sapphire", 
            "Gold", "Diamond", "Emerald", 
            "Titanium", "Meteorite"]

    chances = [2500, 1200, 800, 500, 250, 320, 200, 120, 80, 75, 35, 25, 12, 3]

    def __init__(self, bot):
        self.bot = bot
        self.db = dbm.connect_db("./DataPack/guild.db")

    async def get_ore_inv(self, ctx, person):
        if not self.db.CheckExistence("ores", f"id={str(person.id)}"):
            self.db.cursor.execute(f"""INSERT INTO ores VALUES('{str(person.id)}', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);""")
            self.db.Save()
        self.db.SelectRowData("ores", f"id={str(person.id)}")
        data = self.db.cursor.fetchone()
        description_bag = """
        ```{:<12} : {} ({}%)\n{:<12} : {} ({}%)\n{:<12} : {} ({}%)\n{:<12} : {} ({}%)\n{:<12} : {} ({}%)\n{:<12} : {} ({}%)\n{:<12} : {} ({}%)\n{:<12} : {} ({}%)\n{:<12} : {} ({}%)\n{:<12} : {} ({}%)\n{:<12} : {} ({}%)\n{:<12} : {} ({}%)\n{:<12} : {} ({}%)\n{:<12} : {} ({}%)```""".format(
            "Copper", data[1], float(self.chances[0] / 100),
            "Lead", data[2], float(self.chances[1] / 100),
            "Tin", data[3], float(self.chances[2] / 100),
            "Cobalt", data[4], float(self.chances[3] / 100),
            "Coal", data[6], float(self.chances[5] / 100),
            "Iron", data[5], float(self.chances[4] / 100),
            "Silver", data[7], float(self.chances[6] / 100),
            "Ruby", data[8], float(self.chances[7] / 100),
            "Sapphire", data[9], float(self.chances[8] / 100),
            "Gold", data[10], float(self.chances[9] / 100),
            "Diamond", data[11], float(self.chances[10] / 100),
            "Emerald", data[12], float(self.chances[11] / 100),
            "Titanium", data[13], float(self.chances[12] / 100),
            "Meteorite", data[14], float(self.chances[13] / 100)
        )
        emb = discord.Embed(title=f"💎 {person.display_name}'s Bag", description=description_bag, colour=discord.Colour(WHITE))
        emb.set_thumbnail(url="https://webstockreview.net/images/clipart-diamond-bunch-7.png")
        await ctx.send(embed=emb)

    def rarity_randomize(self):
        _list_of_gotem = []
        if self.approve(self.chances[0]) is True:
            _list_of_gotem.append("Copper")
        if self.approve(self.chances[1]) is True:
            _list_of_gotem.append("Lead")
        if self.approve(self.chances[2]) is True:
            _list_of_gotem.append("Tin")
        if self.approve(self.chances[3]) is True:
            _list_of_gotem.append("Cobalt")
        if self.approve(self.chances[4]) is True:
            _list_of_gotem.append("Iron")
        if self.approve(self.chances[5]) is True:
            _list_of_gotem.append("Coal")
        if self.approve(self.chances[6]) is True:
            _list_of_gotem.append("Silver")
        if self.approve(self.chances[7]) is True:
            _list_of_gotem.append("Ruby")
        if self.approve(self.chances[8]) is True:
            _list_of_gotem.append("Sapphire")
        if self.approve(self.chances[9]) is True:
            _list_of_gotem.append("Gold")
        if self.approve(self.chances[10]) is True:
            _list_of_gotem.append("Diamond")
        if self.approve(self.chances[11]) is True:
            _list_of_gotem.append("Emerald")
        if self.approve(self.chances[12]) is True:
            _list_of_gotem.append("Titanium")
        if self.approve(self.chances[13]) is True:
            _list_of_gotem.append("Meteorite")
        if len(_list_of_gotem) == 0:
            return None
        else:
            return random.choice(_list_of_gotem)

    @staticmethod
    def approve(percentage: int) -> bool:
        """Randomize from 0 - 10000"""
        approved = random.randint(0, 10000)
        failed = 10000 - percentage
        if failed < approved:
            return True
        else:
            return False
        
    @commands.command(aliases=['mine'])
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def dig(self, ctx):
        # Digging Animation
        dig = "Dig... "
        emb = discord.Embed(title="⛏️ Mining...", description=dig, colour=discord.Colour(WHITE))
        queing = await ctx.send(embed=emb)
        await asyncio.sleep(0.5)
        for i in range(2):
            dig += "Dig... "
            emb = discord.Embed(title="⛏️ Mining...", description=dig, colour=discord.Colour(WHITE))
            await queing.edit(embed=emb)
            await asyncio.sleep(0.5)

        # Getting an Ore
        ore = self.rarity_randomize()
        failed = ["It's just a Rock... Throw it away!", 
        "Punching rock is hard, did you realize you forgot your pickaxe?", 
        "OMG Ghost! RUN!!!",
        "You went into the Lava, I told you not to dig straight down :v"]
        if ore is None:
            emb = discord.Embed(title="💨 Better Luck Next Time...", description=f"{random.choice(failed)}", colour=discord.Colour(WHITE))
            await queing.edit(embed=emb)
        else:
            emb = discord.Embed(title="💎 Bling!", description="Yay, You have got **{}**!".format(ore), colour=discord.Colour(WHITE))
            if not self.db.CheckExistence("ores", f"id={str(ctx.message.author.id)}"):
                self.db.cursor.execute(f"""INSERT INTO ores VALUES('{ctx.message.author.id}', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);""")
            self.db.cursor.execute(f"UPDATE ores SET {ore.lower()}={ore.lower()} + 1 WHERE id=:uid", {"uid":str(ctx.message.author.id)})
            self.db.Save()
            await queing.edit(embed = emb)

    @dig.error
    async def mine_error(self, ctx, error):
        emb = discord.Embed(colour=discord.Colour(WHITE))
        if isinstance(error, commands.CommandOnCooldown):
            emb.add_field(name="💤 Zzzz... 💤", value="You have a fatigue, take a rest for **{0:.2f}** s.".format(error.retry_after))
            this_msg_coroute = await ctx.send(embed=emb)
            await asyncio.sleep(3)
            await this_msg_coroute.delete()

    @commands.command(aliases=['ore'])
    async def ores(self, ctx, person: discord.Member):
        await self.get_ore_inv(ctx, person)

    @ores.error
    async def ores_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await self.get_ore_inv(ctx, ctx.message.author)

def setup(bot):
    bot.add_cog(Mine(bot))