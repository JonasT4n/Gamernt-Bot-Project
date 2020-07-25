"""
@Copyright Gamern't RPG 2020
----------------------------
Attribute Package. Editable.
"""
DATA_LVL: dict = {}
PERLEVEL: int = 50
MAXLEVEL: int = 60
MAXSKILL: int = 30

LVL_INIT: dict = {
    "STR": {
        1: 324,
        "dec": 8,
        },
    "END": {
        1: 480,
        "dec": 10,
        "eff": "HP"
        },
    "AGI": {
        1: 2000,
        "dec": 25,
        },
    "FOC": {
        1: 1200,
        "dec": 20,
        },
    "ITE": {
        1: 300,
        "dec": 8,
        },
    "WIS": {
        1: 320,
        "dec": 8,
        }
    }

start_rpg: dict = {
    "CHARID": 1,
    "CLASSID": 1,
    "TRP": 0,
    "LVL": 0,
    "EXP": 0,
    "win-count": 0,
    "lost-count": 0,
    "skill-point": 0,
    "MAX-ITEM-HOLD": 10,
    "PRIM-STAT": {
        "STR": 0,
        "END": 0,
        "AGI": 0,
        "FOC": 0,
        "ITE": 0,
        "WIS": 0
        },
    "moves": [],
    "backpack.item": [],
    "equip": [],
    }
