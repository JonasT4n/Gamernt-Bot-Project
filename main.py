import discord
import os
from discord.ext import commands
from Settings.MongoManager import MongoManager
from Settings.MyUtility import get_prefix
from Settings.StaticData import TOKEN

def check_guild_prefix(bot: commands.Bot, message: discord.Message):
    """
    
    Check Current Guild Prefix in Command or Message.
    
    """
    if not isinstance(message.channel, discord.DMChannel):
        guild: discord.Guild = message.guild
        pref: str = get_prefix(guild.id)
        if message.content[0:len(pref)].lower() == pref.lower():
            return message.content[0:len(pref)]
        else:
            return "This is Not a Prefix for this Server, Try Again later!..."

bot = commands.Bot(command_prefix = check_guild_prefix)
bot.remove_command("help")

if __name__ == "__main__":
    # Loading Extensions
    for game in os.listdir("./GamePack"):
        if game.endswith(".py"):
            bot.load_extension("GamePack.{}".format(game[:-3]))

    for info in os.listdir("./InformationPack"):
        if info.endswith(".py"):
            bot.load_extension("InformationPack.{}".format(info[:-3]))

    for info in os.listdir("./RPG"):
        if info.endswith(".py"):
            bot.load_extension("RPG.{}".format(info[:-3]))

    # Run the Bot
    bot.run(TOKEN)

    # Bot Stopped Working
    print("{:^50}".format("~ Session Ended, OOF! ~"))