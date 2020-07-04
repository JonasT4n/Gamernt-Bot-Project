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

# Attributes

db_for_mbr = MongoManager(collection= "members")
db_for_gld = MongoManager(collection= "guilds")

# Functions

def checkin_member(member_id: int) -> dict:
    """
        
    Check if Member is in the Database.

    Return
    ------
    (dict) => Member Information
    
    """
    query: dict = {"member_id": str(member_id)}
    u_data = db_for_mbr.FindObject(query)
    if u_data is None:
        nd: dict = new_member_data
        nd["member_id"] = str(member_id)
        db_for_mbr.InsertOneObject(nd)
        return nd
    else:
        del u_data[0]['_id']
        return u_data[0]

def checkin_guild(guild_id: int) -> dict:
    """
        
    Check if Guild is in the Database.

    Return
    ------
    (dict) => Guild Information
    
    """
    query: dict = {"guild_id": str(guild_id)}
    u_data = db_for_gld.FindObject(query)
    if u_data is None:
        gd: dict = new_guild_data
        gd["guild_id"] = str(guild_id)
        db_for_gld.InsertOneObject(gd)
        return gd
    else:
        del u_data[0]['_id']
        return u_data[0]

def get_prefix(guild_id: int) -> str:
    """
    
    Get Current Prefix in this Guild.
    
    """
    guild_data: dict = checkin_guild(guild_id)
    return guild_data["prefix"]

def set_prefix(guild_id: int, new_prefix: str):
    """
    Set Guild Prefix and Overwrite to Mongo Data.

    Args:
        `guild_id` (int): ID from server Guild.
        `new_prefix` (str): small string prefix for command.
    """
    db_for_gld.SetObject(
        {"guild_id":str(guild_id)}, 
        {"prefix": new_prefix}
        )

def rpg_init(member_id: int):
    mbr_data: dict = checkin_member(member_id)
    db_for_mbr.SetObject(
        {"member_id": mbr_data["member_id"]},
        start_rpg
        )

def rpg_close(member_id: int):
    mbr_data: dict = checkin_member(member_id)
    default_data: dict = start_rpg
    for el in default_data:
        subdata = None
        dlist: list = el.split(".")
        for n in dlist:
            if subdata is None:
                subdata = mbr_data[n]
            else:
                subdata = subdata[n]
        default_data[el] = subdata
    db_for_mbr.UnsetItem(
        {"member_id": mbr_data["member_id"]},
        default_data
        )

def circular_mask(name: str, size: list or tuple):
    mask = Image.new("RGBA", size, color= (255, 255, 255, 0))
    draw = ImageDraw.Draw(mask)

    draw.ellipse([(0, 0), size], fill= (255, 255, 255))
    mask.save(name)

def background_init(filename: str, outputname: str, *, size= (540, 100), centering= (0.67, 0.67)):
    bar_bg = Image.new("RGB", size)
    bg = Image.open(filename)
    output = ImageOps.fit(bg, bar_bg.size, centering= centering)
    output.save(outputname)

def is_number(num: str):
    """Check if string contains only number."""
    for word in num:
        if not (48 <= ord(word) < 58):
            return False
    return True

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