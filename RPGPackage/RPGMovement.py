"""
@Copyright Gamern't RPG 2020
----------------------------
Character Movement
"""

import random
from .RPGElemental import checkElement, Elemental, TYPE_ELEMENT

# Type Move Attack
TYPE_ATTACK = {1:"Physical", 2:"Magic"}
TYPE_TARGET = {1:"Single", 2:"Splash"}

# Move Structure
move_structure = {
    "NAME": None, # Name of Move
    "TYPE_ATT": None, # Type Attack in ID
    "ELEMENT": None, # Element Type in ID 
    "TARGET": None, # Target Enemt in ID
    "ATTMSG": None, # Attack Message Information
    "MANA": None, # Required Mana to use it.
    }

def MakeMove(*args, **kwargs):
    """### Arguments
    -------------
    Insert data with following order: `name`(str) `typeatt`(int) `element`(int) `target`(int) `attmsg`(str).
    Or, insert the structure of data in (dict) and pass into the args.

    ### Key Arguments
    -----------------
    `name`(str): the name of `Movement`.
    `typeatt`(int): id of attack type. `element`(int): id of element type. `target`(int): id of target attack type.
    `attmsg`(str): attack message, you can use '<me>' and '<enemy>' in the message, this will automatically replaced into character `name`.
    `owner`(Character): owner of this movement.
    ### Return
    ----------
    (Movement): A base move, the struct inserted automatically.
    """
    # Check arguments
    owner = None if "owner" not in kwargs else kwargs["owner"]
    if len(args) == 1:
        if isinstance(args[0], dict):
            if move_structure.keys() == args[0].keys():
                return Movement(args[0], owner=owner)
        raise AttributeError("not enough argument.")
    if len(args) > 5:
        raise AttributeError("too many argument.")

    # Priority Insertion: Key Argument, Argument
    # Insert Argument
    struct_move: dict = move_structure
    for i in range(len(args)):
        struct_move[list(struct_move.keys())[i]] = args[i]
    # Insert Key Argument
    struct_move["NAME"] = struct_move["NAME"] if "name" not in kwargs else kwargs["name"]
    struct_move["TYPE_ATT"] = struct_move["TYPE_ATT"] if "type_att" not in kwargs else kwargs["type_att"]
    struct_move["ELEMENT"] = struct_move["ELEMENT"] if "element" not in kwargs else kwargs["element"]
    struct_move["TARGET"] = struct_move["TARGET"] if "element" not in kwargs else kwargs["element"]
    struct_move["ATTMSG"] = struct_move["ATTMSG"] if "attmsg" not in kwargs else kwargs["attmsg"]
    struct_move["MANA"] = 0 if "mana" not in kwargs else kwargs["mana"]

    # Check if the structure has been fulfilled
    if None in list(struct_move.values()):
        raise AttributeError("not enough argument.")
    return Movement(struct_move, owner=owner)

class Movement:
    """
    # Player Base Movement
    ----------------------
    """
    _effect_parse: dict = {} # This attibute will be send to the enemy.
    __data: dict # Parsed Data from Constructor
    __type_att: int # Type Attack
    __element: Elemental # Elemental Type
    __target: int # Which Target, 1:Single or 2:Multi
    __attack_msg: str # Attack Message
    __req_mana: int # Required Mana
    __raw_dmg: int # Raw Damage from Damage Process
    __owner = None

    @property
    def GetDetail(self):
        use_mana = False if self.__req_mana == 0 else True
        return {"Name":self.__name, "Type Attack":[self.__type_att, TYPE_ATTACK[self.__type_att]], "Element":[self.__element, self.__element.__class__.__name__], 
                "Target":[self.__target, TYPE_TARGET[self.__target]], "Use Mana": use_mana, "Required Mana":self.__req_mana}

    @property
    def Name(self):
        return self.__name

    @property
    def RawDmg(self):
        return self.__raw_dmg

    @RawDmg.setter
    def RawDmg(self, value: int):
        self.__raw_dmg = value

    def __init__(self, _data: dict, *, owner = None):
        self.__data = _data
        self.__name = _data["NAME"]
        self.__type_att = _data["TYPE_ATT"]
        self.__element = checkElement(_data["ELEMENT"])
        self.__target = _data["TARGET"]
        self.__attack_msg = _data["ATTMSG"]
        self.__req_mana = _data["MANA"]
        self.__owner = owner

    def GetElemental(self):
        return self.__element

    def GetTypeAttID(self):
        return self.__type_att

    def GetTargetID(self):
        return self.__target

    def SetOwner(self, owner):
        self.__owner = owner

    def Use(self, target):
        """## Parameter
        ------------
        `who` (Character): Person who own this move.
        `target` (Character): Use this move at target. 
        """
        # Not enough Mana
        if self.__owner.MANA < self.__req_mana:
            return False

        # List of targets
        if isinstance(target, list):
            # For Single Target
            if len(target) == 1:
                self.RawDmg = self.__owner.GetRandomDamage(self.__type_att, 1)
                target[0].Defend(self)
            # For Multi Target
            elif len(target) > 1:
                for t in range(len(target)):
                    # The First target will get greater damage than others
                    if t == 0:
                        self.RawDmg = self.__owner.GetRandomDamage(self.__type_att, 0.8)
                    else:
                        self.RawDmg = self.__owner.GetRandomDamage(self.__type_att, 0.4)
                    target[t].Defend(self)

        # Only for Single Target
        else:
            self.RawDmg = self.__owner.GetRandomDamage(self.__type_att, 1)
            target.Defend(self)

        # Process Usage
        self.__owner.MANA -= self.__req_mana
        self.__owner.MANA = self.__owner.MAX_MANA if self.__owner.MANA > self.__owner.MAX_MANA else self.__owner.MANA
        self.__owner.Msg = self.TranslateMsg(self.__attack_msg, self.__owner, target)
        return True

    @staticmethod
    def TranslateMsg(msg: str, me, target):
        """Only translate if contains `<me>`/`<enemy>` into several character names."""
        if "<me>" in msg:
            msg = msg.replace("<me>", me.name)
        if "<enemy>" in msg:
            if isinstance(target, list):
                if len(target) > 1:
                    text: str = ""
                    for i in range(len(target)):
                        if i == len(target) - 1:
                            text += f", and {target[i].name}"
                        elif i == 0:
                            text += target[i].name
                        else:
                            text += f", {target[i].name}"
                    msg = msg.replace("<enemy>", text)
                else:
                    msg = msg.replace("<enemy>", target[0].name)
            else:
                msg = msg.replace("<enemy>", target.name)
        return msg
