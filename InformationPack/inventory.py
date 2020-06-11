import discord
import asyncio
from discord.ext import commands
from Settings.StaticData import pickaxe_identity
from Settings.MyUtility import checkin_member, checkin_guild, get_prefix

WHITE = 0xfffffe

class Inventory(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Listener Area

    @commands.Cog.listener()
    async def on_ready(self):
        print("Inventory is Ready!")

    # Checker Area

    def user_check(self, person: discord.User):
        def inner_check(message: discord.Message):
            if person == message.author:
                return True
            else:
                return False
        return inner_check

    # Inventories

    async def main_menu(self, message: discord.Message, person: discord.User) -> bool:
        user_data: dict = checkin_member(person.id)
        menu_embed = discord.Embed(
            title=f"{person.display_name}'s Inventory",
            description=f"👛 Money : {user_data['money']}💲\n1. Ores ⛏️",
            colour=discord.Colour(WHITE)
        )
        menu_embed.set_footer(text="Select by Number to see detail.")
        await message.edit(embed = menu_embed)
        return True

    async def ore_inventory(self, message: discord.Message, person: discord.User) -> bool:
        """Only for Inventory."""
        # Get Member Data
        user_data: dict = checkin_member(person.id)
        user_sack: dict = user_data["backpack"]["ores"]
        pick_level: int = user_data["backpack"]["pickaxe-level"]

        # Get Detail Sack of Ores
        ore_keys: list = list(pickaxe_identity[pick_level]["balance"].keys())
        description_bag: str = "```"
        for i in range(len(ore_keys)):
            ore_name: str = ore_keys[i]
            if i == len(ore_keys) - 1:
                description_bag += "{:.<12}{} ({}%)".format(ore_name, user_sack[ore_name], pickaxe_identity[pick_level]["balance"][ore_name] / 100)
            else:
                description_bag += "{:.<12}{} ({}%)\n".format(ore_name, user_sack[ore_name], pickaxe_identity[pick_level]["balance"][ore_name] / 100)
        description_bag += "```"

        # Edit Menu with This Data Detail
        emb = discord.Embed(
            title= f"💎 {person.display_name}'s' Sack Of Ores", 
            description= f"Pickaxe Level : {pick_level}\n"
                        f"{description_bag}",
            colour= discord.Colour(WHITE)
        )
        emb.set_thumbnail(url= "https://webstockreview.net/images/coal-clipart-bag-coal-6.png")
        emb.set_footer(text= f"Press '0' to go back | You can upgrade your pickaxe by using {get_prefix(message.guild.id)}pickaxeup")
        await message.edit(embed=emb)
        return False

    async def equipment(self, message: discord.Message, person: discord.User):
        return False

    async def items(self, message: discord.Message, person: discord.User):
        return False

    # Commands Area

    @commands.command(name= "inventory", aliases= ["inv"])
    async def _inv(self, ctx: commands.Context, *args):
        on_main_menu: bool = True
        tud: dict = checkin_guild(ctx.guild.id)
        menu_emb = discord.Embed(
            title= f"{ctx.author.display_name}'s Inventory",
            description= f"> 👛 Money : {tud['member'][str(ctx.author.id)]['money']} {tud['currency']['type']}\n"
                        "> ⛏️ 1. Ores \n"
                        "> 🛡️ 2. Equipment\n"
                        "> 🧳 3. Backpack",
            colour= discord.Colour(WHITE)
            )
        menu_emb.set_footer(text= "Select by Number to see detail.")
        handler_message: discord.Message = await ctx.send(embed = menu_emb)
        try:
            while True:
                answered: discord.Message = await self.bot.wait_for(event="message", check=self.user_check(ctx.author), timeout=30.0)
                if answered.content == "1" and on_main_menu:
                    await answered.delete()
                    on_main_menu = await self.ore_inventory(handler_message, ctx.author)
                elif answered.content == "0" and not on_main_menu:
                    await answered.delete()
                    on_main_menu = await self.main_menu(handler_message, ctx.author)
                elif answered.content == "2" and on_main_menu:
                    await answered.delete()
                    on_main_menu = await self.equipment(handler_message, ctx.author)
                elif answered.content == "3" and on_main_menu:
                    await answered.delete()
                    on_main_menu = await self.items(handler_message, ctx.author)
                else:
                    continue
        except asyncio.TimeoutError:
            pass

    # Others

def setup(bot: commands.Bot):
    bot.add_cog(Inventory(bot))