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

class Events(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.guild_col = MongoManager(collection= "guilds")
        self.member_col = MongoManager(collection= "members")

    # Task Section

    @tasks.loop(seconds= 3)
    async def change_status(self):
        await self.bot.change_presence(activity= discord.Game(name= next(STATUS)))

    @tasks.loop(hours= 3)
    async def clean_picture_cache(self):
        for i in os.listdir('.'):
            if i.endswith(".jpg"):
                os.remove(i)

    def cog_unload(self):
        self.change_status.cancel()
        self.clean_picture_cache.cancel()

    # Events Listener Section

    @commands.Cog.listener()
    async def on_ready(self):
        self.change_status.start()

    @commands.Cog.listener()
    async def on_disconnect(self):
        self.change_status.cancel()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Built-in Event Message."""
        if not isinstance(message.channel, discord.DMChannel):
            # Get Prefix by tagging Bot
            pref: str = get_prefix(message.guild.id)
            if str(self.bot.user.id) in message.content:
                emb = discord.Embed(
                    title= f"Your Server Prefix is {pref}\n"
                        f"type {pref}help for commands.", 
                    color= discord.Color(WHITE)
                    )
                await message.channel.send(embed=emb)

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