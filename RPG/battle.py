import discord
import math
import random
from discord.ext import commands
from Settings.MongoManager import MongoManager
from Settings.MyUtility import checkin_member, convert_rpg_substat, Duelist, get_prefix

WHITE = 0xfffffe

class Battle(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.mongodbm = MongoManager(collection="members")

    # Listener Area

    @commands.Cog.listener()
    async def on_ready(self):
        print("Battle RPG System is Ready!")

    # Command Area

    @commands.command(name= "battle", aliases= ['btl'], pass_context= True)
    async def _battle(self, ctx: commands.Context, *args):
        if len(args) == 0:
            await self.print_help(ctx.channel)
        else:
            pass

    # Others

    @staticmethod
    async def print_help(channel: discord.TextChannel):
        pref: str = get_prefix(channel.guild.id)
        emb = discord.Embed(
            title= "⚔️ Battlefield | Help",
            description= f"A Turnbase RPG game, you will pay it manually, don't forget to {pref}.start to start your progress.",
            colour= discord.Colour(WHITE)
            )
        emb.add_field(
            name= "Command :",
            value= f"{pref}.battle <mode>",
            inline= False
            )
        emb.add_field(
            name= "Mode :",
            value= "`1v1` - 1 vs 1 Player"
                "`2v2` - 2 vs 2 Player"
                "`3v3` - 3 vs 3 Player",
            inline= False
            )
        emb.set_footer(text= f"Example Command : {pref}.battle 1v1")
        await channel.send(embed= emb)
        
def setup(bot: commands.Bot):
    bot.add_cog(Battle(bot))