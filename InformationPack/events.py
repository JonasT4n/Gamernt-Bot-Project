import discord
import os
import shutil
from itertools import cycle
from discord.ext import commands, tasks
from Settings.MongoManager import MongoManager
from Settings.MyUtility import get_prefix, checkin_member, checkin_guild

WHITE = 0xfffffe
STATUS = cycle(["Tag Me for Prefix", "Not Game"])

class Events(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.guild_col = MongoManager(collection = "guilds")
        self.member_col = MongoManager(collection = "members")

    # Method

    def clear_cache_in_folder(self, path: str):
        for i in os.listdir(path):
            if i == "__pycache__":
                shutil.rmtree(f"{path}/__pycache__")
            if os.path.isdir(f"{path}/{i}"):
                clear_cache(f"{path}/{i}")

    # Task Section

    @tasks.loop(seconds = 5)
    async def change_status(self):
        await self.bot.change_presence(activity=discord.Game(name=next(STATUS)))

    @tasks.loop(hours = 1)
    async def clear_cache(self):
        clear_cache_in_folder(".")

    # Events Listener Section

    @commands.Cog.listener()
    async def on_ready(self):
        self.change_status.start()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        
        Builtin Event Message.
        
        """
        if not isinstance(message.channel, discord.DMChannel):
            guild_data: dict = checkin_guild(message.guild.id)
            if not str(message.author.id) in guild_data["members"]:
                self.guild_col.UpdateObject({"guild_id": str(message.guild.id)}, {
                    "$push" : {
                        "members": str(message.author.id)
                    }
                })
            
            # Get Prefix by tagging Bot
            pref: str = get_prefix(message.guild.id)
            if str(self.bot.user.id) in message.content:
                emb = discord.Embed(
                    title=f"Your Server Prefix is {pref}\ntype {pref}help for commands.", 
                    color=discord.Color(WHITE)
                )
                await message.channel.send(embed = emb)

            # Chat Money
            if not message.content.startswith(pref):
                user_data: dict = checkin_member(message.author.id)
                self.member_col.IncreaseItem(
                    {"member_id": str(message.author.id)}, 
                    {"money": 10}
                )

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.MissingRequiredArgument):
            return
        if isinstance(error, commands.CommandOnCooldown):
            return
        raise error

def setup(bot: commands.Bot):
    bot.add_cog(Events(bot))