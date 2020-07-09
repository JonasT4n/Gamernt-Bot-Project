import discord
import asyncio
import random
from discord.ext import commands
from Settings.MyUtility import checkin_member, get_prefix, db_mbr
from Settings.StaticData import pickaxe_identity

WHITE = 0xfffffe

class Mine(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Command Area
        
    @commands.command(name="dig", aliases=['mine'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _dig(self, ctx):
        person: discord.User = ctx.author
        user_bag = checkin_member(person)
        if user_bag is not None:
            # Digging Animation
            dig = "Dig... "
            emb = discord.Embed(
                title="⛏️ Mining...", 
                description=dig, 
                colour=WHITE
                )
            queing: discord.Message = await ctx.send(embed=emb)
            await asyncio.sleep(0.5)
            for i in range(2):
                dig += "Dig... "
                emb = discord.Embed(
                    title="⛏️ Mining...", 
                    description=dig, 
                    colour=WHITE
                    )
                await queing.edit(embed=emb)
                await asyncio.sleep(0.5)

            # Getting an Ore
            ore: str = self.rarity_randomize(user_bag["backpack"]["pickaxe-level"])
            failed = [
                "It's just a Rock... Throw it away!", 
                "Punching rock is hard, did you realize you forgot your pickaxe?", 
                "OMG Ghost! RUN!!!",
                "You went into the Lava, I told you not to dig straight down :v"
                ]

            # Print Out Result
            if ore is None:
                emb = discord.Embed(
                    title="💨 Better Luck Next Time...", 
                    description=f"{random.choice(failed)}", 
                    colour=WHITE
                    )
                await queing.edit(embed=emb)
            else:
                emb = discord.Embed(
                    title="💎 Bling!", 
                    description=f"Yay {person.name}, You have got __**{ore}**__!", 
                    colour=WHITE
                    )
                emb.set_footer(text=f"Check {get_prefix(ctx.guild)}ore to see your collection.")
                await queing.edit(embed=emb)
                db_mbr.IncreaseItem({"member_id":str(person.id)}, {f"backpack.ores.{ore}": 1}) # Save Data

    @commands.command(name="pickaxeup")
    async def _pickaxeup(self, ctx: commands.Context):
        # Initialize Things
        able_upgrade: bool = True
        user_data = checkin_member(ctx.author)
        if user_data is not None:
            sack_of_ores: dict = user_data["backpack"]["ores"]
            pick_level: int = user_data["backpack"]["pickaxe-level"]
            requirement: dict = pickaxe_identity[pick_level + 1]["requirement"]
            list_required: list = list(requirement.keys())

            # Check if it is Able to Upgrade
            req_text: str = ""
            for i in range(len(list_required)):
                if sack_of_ores[list_required[i]] < requirement[list_required[i]]:
                    able_upgrade = False
                if i == len(list_required) - 1:
                    req_text += f"> `{list_required[i]}`: {sack_of_ores[list_required[i]]}/{requirement[list_required[i]]}"
                else:
                    req_text += f"> `{list_required[i]}`: {sack_of_ores[list_required[i]]}/{requirement[list_required[i]]}\n"

            # Print Out Requirements and Confirmation
            emb = discord.Embed(
                title=f"Upgrade to Level {pick_level + 1} ⛏️?", 
                description=f"**Requirements** : \n{req_text}",
                colour=WHITE
                )
            if not able_upgrade:
                emb.set_footer(text="Sorry, Not Enough Materials.")
                await ctx.send(embed=emb)
            else:
                menus: list = ["✅", "❌"]
                emb.set_footer(text="Will you Upgrade it? add ✅ to proceed or ❌ to abort")
                hm: discord.Message = await ctx.send(embed=emb)
                for i in menus:
                    await hm.add_reaction(i)
                try:
                    r: discord.Reaction
                    u: discord.User
                    r, u = await self.bot.wait_for(
                        event="reaction_add", 
                        check=lambda reaction, user: True if str(reaction.emoji) in menus and user == ctx.author else False, 
                        timeout=30.0
                        )
                    if str(r.emoji) == "✅":
                        await hm.delete()
                        emb = discord.Embed(
                            title=f"Your ⛏️ has been Upgraded to level {pick_level + 1}", 
                            description=f"See the Stat in g.inv",
                            colour=WHITE
                            )
                        await ctx.send(embed=emb)
                        db_mbr.IncreaseItem({"member_id": str(ctx.author.id)}, {"backpack.pickaxe-level": 1})
                        for ore in requirement:
                            db_mbr.IncreaseItem({"member_id": str(ctx.author.id)}, {f"backpack.ores.{ore}": -requirement[ore]})
                    else:
                        emb.set_footer(text="Ok, Next Time!")
                        await hm.edit(embed=emb)
                except asyncio.TimeoutError:
                    pass

    # Error Command Handler

    @_dig.error
    async def mine_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, commands.CommandOnCooldown):
            emb = discord.Embed(
                title="💤 Zzzz... 💤",
                description="Calm Down, i need to take a rest for **{0:.2f}** second(s)".format(error.retry_after),
                colour=WHITE
                )
            this_msg_coroute: discord.Message = await ctx.send(embed=emb)
            await asyncio.sleep(3)
            await this_msg_coroute.delete()

    # Others

    def rarity_randomize(self, pickaxe_level: int) -> str:
        """
        This is the Place Where you Mine Ores, Are you Lucky enough?

            Returns :
                (str) => Name of Ore you have Got
        """
        _list_of_gotem = []
        ore_keys: list = list(pickaxe_identity[pickaxe_level]["balance"].keys())
        for i in range(len(ore_keys)):
            ore_name: str = ore_keys[i]
            if self.approve(pickaxe_identity[pickaxe_level]["balance"][ore_name]) is True:
                _list_of_gotem.append(ore_name)
        if len(_list_of_gotem) == 0:
            return None
        else:
            return random.choice(_list_of_gotem)
        
    @staticmethod
    def approve(percentage: int) -> bool:
        """Randomize from 0 - 10000."""
        approved = random.randint(0, 10000)
        failed = 10000 - percentage
        if failed < approved:
            return True
        else:
            return False

def setup(bot: commands.Bot):
    bot.add_cog(Mine(bot))