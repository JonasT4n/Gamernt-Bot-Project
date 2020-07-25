"""
@Copyright Gamern't RPG 2020
----------------------------
This Script only use for this bot and cannot reuse it.
"""

import math
import random
import discord
import asyncio
import PIL
from PIL import Image, ImageDraw, ImageOps
from .MongoManager import MongoManager
from .StaticData import new_guild_data, new_member_data
from RPGPackage.RPGModule import *

# Attributes

db_mbr = MongoManager(collection="members")
db_gld = MongoManager(collection="guilds")
db_rpt = MongoManager(collection="report")

# Functions

def checkin_member(user: discord.User):
    """
    Check if Member is in the Database.

    Returns
    ------
    (`dict`) => Member Information.
    (`None`) => If User is Bot and Data won't come up.
    """
    if not user.bot:
        query: dict = {"member_id": str(user.id)}
        u_data = db_mbr.FindObject(query)
        if u_data is None:
            nd: dict = new_member_data
            nd["member_id"] = str(user.id)
            db_mbr.InsertOneObject(nd)
            return nd
        else:
            del u_data[0]["_id"]
            return u_data[0]
    else:
        return None

def checkin_guild(guild: discord.Guild) -> dict:
    """
    Check if Guild is in the Database.

    Return
    ------
    (dict) => Guild Information.
    """
    query: dict = {"guild_id": str(guild.id)}
    u_data = db_gld.FindObject(query)
    if u_data is None:
        gd: dict = new_guild_data
        gd["guild_id"] = str(guild.id)
        db_gld.InsertOneObject(gd)
        return gd
    else:
        del u_data[0]["_id"]
        return u_data[0]

def get_prefix(guild: discord.Guild) -> str:
    """Get Current Prefix in this Guild."""
    guild_data: dict = checkin_guild(guild)
    return guild_data["prefix"]

def set_prefix(guild: discord.Guild, new_prefix: str):
    """
    Set Guild Prefix and Overwrite to Mongo Data.

    Args:
        `guild_id` (int): ID from server Guild.
        `new_prefix` (str): small string prefix for command.
    """
    db_gld.SetObject({"guild_id":str(guild.id)}, {"prefix": new_prefix})

def circular_mask(name: str, size: list or tuple):
    mask = Image.new("RGBA", size, color=(255, 255, 255, 0))
    draw = ImageDraw.Draw(mask)

    draw.ellipse([(0, 0), size], fill=(255, 255, 255))
    mask.save(name)

def background_init(filename: str, outputname: str, *, size=(540, 100), centering=(0.67, 0.67)):
    bar_bg = Image.new("RGB", size)
    bg = Image.open(filename)
    output = ImageOps.fit(bg, bar_bg.size, centering=centering)
    output.save(outputname)

def is_number(num: str):
    """Check if string contains only number."""
    for word in range(len(num)):
        if word == 0 and num[word] == "-":
            continue
        if not (48 <= ord(num[word]) < 58):
            return False
    return True

def checkClassID(person: discord.User):
    """Check class ID from Discord User."""
    mbr_data = checkin_member(person)
    if mbr_data is not None:
        # If Member registered
        if 'CLASSID' in mbr_data:
            # Character Warrior
            if mbr_data["CLASSID"] == 1:
                return Warrior(person.id, person.name, _data=mbr_data)
            # Character Mage
            elif mbr_data["CLASSID"] == 2:
                return Mage(person.id, person.name, _data=mbr_data)
    classes: list = [Warrior(person.id, person.name), Mage(person.id, person.name)]
    return random.choice(classes)

# Asyncronous Functions
async def add_exp(channel: discord.TextChannel, user: discord.User, amount: int):
    """## Parameter
    ------------
    `channel`(discord.TextChannel): broadcast channel.
    `user`(discord.User): user account.
    `amount`(int): amount of Exp.
    """
    mbr_data = checkin_member(user)
    if mbr_data is not None:
        max_exp_on: int = PERLEVEL * (mbr_data["LVL"] + 1)
        # Level Up Announcement
        if max_exp_on <= mbr_data["EXP"] + amount:
            db_mbr.SetObject({"member_id": str(user.id)}, {"EXP": (mbr_data["EXP"] + amount) - max_exp_on})
            db_mbr.IncreaseItem({"member_id": str(user.id)}, {"LVL": 1, "skill-point": 1})
            emb = discord.Embed(title="LEVEL UP!", colour=0xfffffe, 
                                description=f"{user.name}, you are now level **{mbr_data['LVL'] + 1}**!",)
            emb.set_thumbnail(url=user.avatar_url)
            await channel.send(embed=emb)
        else:
            db_mbr.IncreaseItem({"member_id": str(user.id)}, {"EXP": amount})

async def add_money(guild_id: int, user: discord.User, amount: int):
    """## Parameter
    ------------
    `guild_id`(discord.TextChannel): guild id to identify guild currency.
    `user`(discord.User): user account.
    `amount`(int): amount of Money.
    """
    mbr_data = checkin_member(user)
    if mbr_data is not None:
        if str(guild_id) not in mbr_data['backpack']['money']:
            db_mbr.SetObject({'member_id': mbr_data['member_id']}, {f'backpack.money.{str(guild_id)}': 0})
        db_mbr.IncreaseItem({'member_id': mbr_data['member_id']}, {f'backpack.money.{str(guild_id)}': amount})

async def send_batte_hint(user: discord.User, user_char: Character):
    emb = discord.Embed(title="⚔️ Battle Hint", colour=0xfffffe, 
                        description=f"Send these messages to do some actions in battlefield.\n"
                        f"> `use normal <target>` - Use a normal character attack on target.\n"
                        f"> `use <custom> <target>` - Use a custom moves you have learned on target.\n"
                        f"> `use <item> <target>` - Use an item at target.")
    custom_moves_description: str = ""
    if len(user_char._custom_moves) == 0:
        custom_moves_description = "```You haven't learned any custom move.```"
    else:
        for move in range(len(user_char._custom_moves)):
            if move == len(user_char._custom_moves) - 1:
                custom_moves_description += f"> {move + 1}. {user_char._custom_moves[move].Name}"
            else:
                custom_moves_description += f"> {move + 1}. {user_char._custom_moves[move].Name}\n"
    emb.add_field(name="Your Custom Moves", value=custom_moves_description, inline=False)
    emb.set_author(name=f"{user_char.name} the {user_char.ClassName}", 
                   icon_url=user.avatar_url)
    await user.send(embed=emb)

# Classes
class Queue:
    """## Queue Structure
    ------------------
    Asynchronous Queue in Data Structure.

    This Class only for Sending the Image that has been made by Image Generator.
    The Script is Reuseable.
    """
    # Attribute
    entry: dict = {}

    # Methods
    def pop(self) -> dict:
        pass

    def push(self, data: dict):
        pass
