"""

@Copyright Gamern't RPG 2020
----------------------------
This Script only use for this bot and cannot reuse it.

"""

import math
import random
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

def convert_rpg_substat(stat: dict, *, return_value= False):
    """
    
    Parameter
    ---------
    A built-in dictionary, the data should be Following\n
    stat => { HP: 10000, DEF: 10000, SPD: 10000, ATT: 10000, CRIT: 10000 }\n
    (Optional) return_value => will return tyhe value if True, default is false

    Return
    ------
    (None)
    
    """
    stat["HP"] = math.ceil(stat["HP"] * (8) / 100)
    stat["DEF"] = math.ceil(stat["DEF"] * (1) / 100)
    stat["SPD"] = math.ceil(stat["SPD"] * (1/10) / 100)
    stat["MIN-ATT"] = math.ceil(stat["ATT"] * (12/10) / 100)
    stat["MAX-ATT"] = math.ceil(stat["ATT"] * (15/10) / 100)
    stat.pop("ATT")
    stat["CRIT"] = math.ceil(stat["CRIT"] * (5/100) / 100)
    if return_value is True:
        return stat

# Classes

class Duelist:

    HP: int = 800
    DEF: int = 100
    SPD: int = 10
    MIN_ATT: int = 120
    MAX_ATT: int = 150
    CRIT_CHANCE: int = 5

    def __init__(self, uid: int):
        mbr_data: dict = checkin_member(uid)
        if "MAX-STAT" in mbr_data:
            stat: dict = convert_rpg_substat(mbr_data["MAX-STAT"], return_value= True)
            self.HP = stat["HP"]
            self.DEF = stat["DEF"]
            self.SPD = stat["SPD"]
            self.MIN_ATT = stat["MIN-ATT"]
            self.MAX_ATT = stat["MAX-ATT"]
            self.CRIT_CHANCE = stat["CRIT"]

    def attack(self, target):
        """
        
        Parameters
        ---------
        target (Duelist) : Target Attack

        Returns
        -------
        (int) : Damage Dealt Information
        
        """
        att_multi = 1.2
        def_multi = 1
        spd_luck = random.randint(1, 100)
        if random.randint(1, 100) <= self.CRIT_CHANCE:
            att_multi += 0.8
        if spd_luck <= target.SPD:
            att_multi -= 1
        if spd_luck <= target.SPD // 3:
            att_multi = 0
        damage = math.ceil(random.randint(self.MIN_ATT, self.MAX_ATT) * att_multi * 100 / (100 + (target.DEF * def_multi)))
        target.HP -= damage
        return damage