import discord
import os
import shutil
import random
from itertools import cycle
from discord.ext import commands, tasks
from Settings.MongoManager import MongoManager
from Settings.MyUtility import get_prefix, checkin_member, checkin_guild

WHITE = 0xfffffe
STATUS = cycle(["Tag Me for Prefix", "Not Game"])

def clear_caches_folder(path: str):
    for i in os.listdir(path):
        if i == "__pycache__":
            shutil.rmtree(f"{path}/__pycache__")
        if os.path.isdir(f"{path}/{i}"):
            clear_caches_folder(f"{path}/{i}")

class Events(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.guild_col = MongoManager(collection= "guilds")
        self.member_col = MongoManager(collection= "members")

    # Task Section

    @tasks.loop(seconds= 3)
    async def change_status(self):
        await self.bot.change_presence(activity= discord.Game(name= next(STATUS)))

    @tasks.loop(hours = 24)
    async def clear_cache(self):
        global clear_caches_folder
        clear_caches_folder(".")

    # Events Listener Section

    @commands.Cog.listener()
    async def on_ready(self):
        self.change_status.start()
        self.clear_cache.start()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        
        Built-in Event Message.
        
        """
        if not isinstance(message.channel, discord.DMChannel):
            guild_data: dict = checkin_guild(message.guild.id)
            if not str(message.author.id) in guild_data["member"]:
                self.guild_col.SetObject({"guild_id": str(message.guild.id)}, {
                    f"member.{str(message.author.id)}.money": 0
                    })
            # Get Prefix by tagging Bot
            pref: str = get_prefix(message.guild.id)
            if str(self.bot.user.id) in message.content:
                emb = discord.Embed(
                    title= f"Your Server Prefix is {pref}\n"
                        f"type {pref}help for commands.", 
                    color= discord.Color(WHITE)
                    )
                await message.channel.send(embed = emb)
            # Chat Money
            if not message.content.startswith(pref) and not message.author.bot:
                get_money: int = random.randint(guild_data["currency"]["chat-min"], guild_data["currency"]["chat-max"])
                self.guild_col.IncreaseItem({"guild_id": str(message.guild.id)}, {
                    f"member.{str(message.author.id)}.money": get_money
                    }) 

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