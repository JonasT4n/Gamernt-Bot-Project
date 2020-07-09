import discord
import asyncio
from discord.ext import commands
from Settings.StaticData import pickaxe_identity
from Settings.MyUtility import checkin_member, checkin_guild, get_prefix

WHITE = 0xfffffe

class Inventory(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Inventories

    async def main_menu(self, message: discord.Message, person: discord.User):
        tud: dict = checkin_guild(message.guild)
        menu_emb = discord.Embed(
            title=f"{message.author.display_name}'s Inventory",
            description=f"👛 Wallet\n"
                        "⛏️ Ores \n"
                        "🛡️ Equipment\n"
                        "🧳 Backpack Items\n"
                        "🔙 Go Back to Menu",
            colour=WHITE
            )
        menu_emb.set_footer(text="Select Option Below to see the Detail")
        await message.edit(embed=menu_emb)

    async def ore_inventory(self, message: discord.Message, person: discord.User):
        """Only for Inventory."""
        # Get Member Data
        user_data = checkin_member(person)
        if user_data is not None:
            user_sack: dict = user_data["backpack"]["ores"]
            pick_level: int = user_data["backpack"]["pickaxe-level"]

            # Get Detail Sack of Ores
            ore_keys: list = list(pickaxe_identity[pick_level]["balance"].keys())
            description_bag: str = ""
            for i in range(len(ore_keys)):
                ore_name: str = ore_keys[i]
                if i == len(ore_keys) - 1:
                    description_bag += f"`{ore_name}` : {user_sack[ore_name]} | **{pickaxe_identity[pick_level]['balance'][ore_name] / 100}%**"
                else:
                    description_bag += f"`{ore_name}` : {user_sack[ore_name]} | **{pickaxe_identity[pick_level]['balance'][ore_name] / 100}%**\n"

            # Edit Menu with This Data Detail
            emb = discord.Embed(
                title=f"💎 {person.display_name}'s' Sack Of Ores", 
                description=f"Pickaxe Level : {pick_level}\n"
                            f"{description_bag}",
                colour=WHITE
            )
            emb.set_thumbnail(url="https://webstockreview.net/images/coal-clipart-bag-coal-6.png")
            emb.set_footer(text=f"You can upgrade your pickaxe by using {get_prefix(message.guild)}pickaxeup")
            await message.edit(embed=emb)

    async def equipment(self, message: discord.Message, person: discord.User):
        pass

    async def items(self, message: discord.Message, person: discord.User):
        pass

    async def detail_money(self, message: discord.Message, person: discord.User):
        gdata: dict = checkin_guild(message.guild)
        mbr_data = checkin_member(person)
        if mbr_data is not None:
            emb = discord.Embed(
                description=f"> 👛 Amount : {mbr_data['backpack']['money'][str(message.guild.id)]} {gdata['currency']['type']}",
                colour=WHITE
                )
            emb.set_author(name=person.name, icon_url=person.avatar_url)
            await message.edit(embed=emb)

    # Commands Area

    @commands.command(name="inventory", aliases=["inv"])
    async def _inv(self, ctx: commands.Context):
        menus: list = ['👛', '⛏️', '🛡️', '🧳', '🔙']
        state: str = '🔙'
        menu_emb = discord.Embed(
            title=f"{ctx.author.display_name}'s Inventory",
            description=f"👛 Wallet\n"
                        "⛏️ Sack of Ores\n"
                        "🛡️ Equipped Equipments\n"
                        "🧳 Backpack Items\n"
                        "🔙 Go Back to Menu",
            colour=WHITE
            )
        menu_emb.set_footer(text="Select Option Below to see the Detail")
        hm: discord.Message = await ctx.send(embed=menu_emb)
        for i in menus:
            await hm.add_reaction(i)
        try:
            while True:
                r: discord.Reaction
                u: discord.User
                r, u = await self.bot.wait_for(
                    event="reaction_add", 
                    check=lambda reaction, user: True if str(reaction.emoji) in menus and str(reaction.emoji) != state 
                            and user == ctx.author else False, 
                    timeout=30.0
                    )
                # Detail Money
                if str(r.emoji) == '👛':
                    state = '👛'
                    await self.detail_money(hm, ctx.author)
                # Sack of Ores
                elif str(r.emoji) == '⛏️':
                    state = '⛏️'
                    await self.ore_inventory(hm, ctx.author)
                # Equipped Equipments
                elif str(r.emoji) == '🛡️':
                    state = '🛡️'
                    await self.equipment(hm, ctx.author)
                # Backpack Items
                elif str(r.emoji) == '🧳':
                    state = '🧳'
                    await self.items(hm, ctx.author)
                # Go Back to Main Menu
                elif str(r.emoji) == '🔙':
                    state = '🔙'
                    await self.main_menu(hm, ctx.author)
                await r.remove(u)
        except asyncio.TimeoutError:
            pass

    @commands.command(name="balance", aliases=["bal"])
    async def _bal(self, ctx: commands.Context):
        hm: discord.Message = await ctx.send(embed=discord.Embed(colour= discord.Colour(WHITE)))
        async with ctx.typing():
            await self.detail_money(hm, ctx.author)

    @commands.command(name="ores", aliases=['ore'])
    async def _ore(self, ctx: commands.Context):
        hm: discord.Message = await ctx.send(embed=discord.Embed(colour= discord.Colour(WHITE)))
        async with ctx.typing():
            await self.ore_inventory(hm, ctx.author)

    # Others

def setup(bot: commands.Bot):
    bot.add_cog(Inventory(bot))