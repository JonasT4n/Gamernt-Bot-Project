"""@Copyright Gamen't RPG 2020
---------------------------
Main dish.
"""
import discord
import os
from discord.ext import commands
from Settings.MongoManager import MongoManager
from Settings.MyUtility import get_prefix
from Settings.StaticData import TOKEN
from RPGPackage.RPGAttribute import DATA_LVL, LVL_INIT, MAXSKILL

def check_guild_prefix(bot: commands.Bot, message: discord.Message):
    """Check Current Guild Prefix in Command or Message."""
    if not isinstance(message.channel, discord.DMChannel):
        pref: str = get_prefix(message.guild)
        if message.content[0:len(pref)].lower() == pref.lower():
            return message.content[0:len(pref)]
        else:
            return "This is Not a Prefix for this Server, Try Again later!..."

bot = commands.Bot(command_prefix = check_guild_prefix)
bot.remove_command("help")

if __name__ == "__main__":
    # Initialize RPG Attribute
    for i in LVL_INIT:
        DATA_LVL[i] = {"LVL": {}, "SUM": {}}
        for j in range(0, MAXSKILL + 1):
            if j == 0:
                DATA_LVL[i]["LVL"][j] = 0
                DATA_LVL[i]["SUM"][j] = 0
            elif j == 1:
                DATA_LVL[i]["LVL"][j] = LVL_INIT[i][1]
                DATA_LVL[i]["SUM"][j] = LVL_INIT[i][1]
            else:
                DATA_LVL[i]["LVL"][j] = DATA_LVL[i]["LVL"][j - 1] - LVL_INIT[i]["dec"]
                DATA_LVL[i]["SUM"][j] = DATA_LVL[i]["SUM"][j - 1] + DATA_LVL[i]["LVL"][j]

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