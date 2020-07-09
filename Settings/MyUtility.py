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
from Settings.MongoManager import MongoManager
from Settings.StaticData import new_guild_data, new_member_data, start_rpg
from RPGPackage.RPGAttribute import *

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
    for word in num:
        if not (48 <= ord(word) < 58):
            return False
    return True

# Asyncronous Function

async def add_exp(channel: discord.TextChannel, user: discord.User, amount: int):
    mbr_data = checkin_member(user)
    if mbr_data is not None:
        max_exp_on: int = PERLEVEL * (mbr_data["LVL"] + 1)
        if max_exp_on <= mbr_data["EXP"] + amount:
            db_mbr.SetObject({"member_id": str(user.id)}, {"EXP": (mbr_data["EXP"] + amount) - max_exp_on})
            db_mbr.IncreaseItem({"member_id": str(user.id)}, {"LVL": 1, "skill-point": 1})
            # Announcement
            emb = discord.Embed(
                title="LEVEL UP!",
                description=f"{user.name}, you are now level **{mbr_data['LVL'] + 1}**!",
                colour=0xfffffe
                )
            emb.set_thumbnail(url=user.avatar_url)
            await channel.send(embed=emb)
        else:
            db_mbr.IncreaseItem({"member_id": str(user.id)}, {"EXP": amount})

async def add_money(guild_id: int, user: discord.User, amount: int):
    mbr_data = checkin_member(user)
    if mbr_data is not None:
        if str(guild_id) not in mbr_data['backpack']['money']:
            db_mbr.SetObject({'member_id': mbr_data['member_id']}, {f'backpack.money.{str(guild_id)}': 0})
        db_mbr.IncreaseItem({'member_id': mbr_data['member_id']}, {f'backpack.money.{str(guild_id)}': amount})

# Classes

class Queue:
    """

    Queue Structure
    ---------------
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