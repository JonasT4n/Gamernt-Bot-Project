"""@Copyright Gamern't RPG 2020
----------------------------
Equipment part.
"""
from .RPGElemental import checkElement, Elemental

# Add On Structure
add_ons = {
    "SHARPNESS": 0,
    "PROTECTION": 0,
    "HARDNESS": 0,
    "THORN": 0,
    "MAGICPROOF": 0,
    "LIGHTNESS": 0,
    "CURSED": 0,
    "MANASTOCK": 0,
    "FUMBLEPROOF": 0,
    }

# EQ Structure
eq_structure = {
    "NAME": None, # Name of EQ
    "ELEMENT": None, # Type Element by ID
    "ADDON": {} # Add Ons of EQ
    }

def MakeEquipmentStructure(*args, **kwargs) -> dict:
    """### Arguments
    -------------
    Insert data with following order: `name`(str) `element`(int) `addon`(dict)
    ### Key Arguments
    -----------------
    `name`(str): Name of Equipment. `element`(int): element type in ID. `addon`(dict): Adds in Equipment.
    """
    eq_data = eq_structure
    return Equipment(eq_data)

class Equipment:

    __element: Elemental
    __data: dict
    __defend_message: str
    __adds: dict = {}
    __name: str

    def __init__(self, _data: dict):
        self.__data = _data
        self.__element = checkElement(_data["ELEMENT"])
        self.__adds = _data["ADDON"]
        self.__name = _data["NAME"]

    @property
    def GetDetail(self):
        return

    def ProcessDamage(self, enemy_move):
        pass