"""@Copyright Gamern't RPG 2020
----------------------------
Character Base part.
"""
import math
import random
from .RPGMovement import Movement, MakeMove
from .RPGAttribute import *

MAX_OWNED_MOVE = 3
MAX_OWNED_EQ = 1
MAX_OWNED_ITEM = 5

CLASSES: dict = {1: "Warrior", 2: "Mage"}
NATURES: dict = {1: "Normal", 2: "Aggresive", 3: "Careful"}

class Character:

    # Raw Battle Attribute
    RAW_HP: int = 10000
    RAW_DEF: int = 10000
    RAW_SPD: int = 10000
    RAW_ATT: int = 10000
    RAW_CRIT: int = 10000
    RAW_MANA: int = 10000
    RAW_MATT: int = 10000
    RAW_MDEF: int = 10000

    # Actual Battle Attribute
    HP: int
    DEF: int
    SPD: int
    ATT: int
    MIN_ATT: int
    MAX_ATT: int
    CRIT: int
    MANA: int
    MATT: int
    MIN_MATT: int
    MAX_MATT: int
    MDEF: int

    # Max Holder
    MAX_HP: int
    MAX_DEF: int
    MAX_SPD: int
    MAX_ATT: int
    MAX_CRIT: int
    MAX_MANA: int
    MAX_MATT: int
    MAX_MDEF: int

    # Primary Stat
    STRENGTH: int
    ENDURANCE: int
    AGILITY: int
    FOCUS: int
    INTELLIGENCE: int
    WISE: int

    # External Attribute
    _normal_move: Movement # Normal Move
    _custom_moves: list = [] # List if Custom Move
    _eq: list = [] # List of Custom Equipment
    _item: list = [] # List of Items

    # Buff and Fumble
    _att_buffer: float # Attack Buffer
    _def_buffer: float # Defend Buffer
    _buff_crit: float # Critical Attack Buffer, Additional to Attack Buffer
    _buff_force: float # Force Buffer, Additional to Defend Buffer
    _effects: dict = {} # Current effect in character, does it buffer or nerfer?

    # Other Attribute
    __last_dmg_taken: int = 0
    __last_att_isCrit: bool = False
    __characteristic: str
    __msg: str
    __data: dict

    @property
    def Msg(self):
        return self.__msg

    @Msg.setter
    def Msg(self, msg: str):
        self.__msg = msg

    @property
    def LastDamageTaken(self):
        return self.__last_dmg_taken

    @property
    def LastAttIsCrit(self):
        return self.__last_att_isCrit

    @property
    def ClassName(self):
        return f"{self.__characteristic} {self.__class__.__name__}"

    def __init__(self, uid: int, name: str, *, _data: dict = None):
        self.id = uid
        self.name = name
        self.__data = _data
        # Get Characteristic from database if exists
        if _data is not None:
            self.__checkCharacter(_data['CHARID'])
            self.__checkPrimSkill(_data['PRIM-STAT'])
            self._custom_moves = [MakeMove(n, owner=self) for n in _data["moves"]]
        else:
            self.__checkCharacter(random.randint(1, 3))

    def GetCritical(self) -> bool:
        if random.randint(1, 100) < self.CRIT:
            self.__last_att_isCrit = True
            return True
        else:
            self.__last_att_isCrit = False
            return False

    def GetRandomDamage(self, type_att: int, multiplier: float) -> int:
        # Type Attack Physical
        att_buff = self._buff_crit if self.GetCritical() is True else 0
        if type_att == 1:
            return math.ceil(100 * random.randint(self.MIN_ATT, self.MAX_ATT) * (self._att_buffer + att_buff) * multiplier)
        # Type Attack Magic
        if type_att == 2:
            return math.ceil(100 * random.randint(self.MIN_MATT, self.MAX_MATT) * (self._att_buffer + att_buff) * multiplier)

    def Defend(self, enemy_move: Movement):
        """Defend Against the Attack.
        ## Parameter
        ---------
        `attack_type`(int): type attack.
        `raw_dmg`(int): receive raw damage, this will be defend by this character.
        ## Note
        -------
        You can get this Info from method `LastDamageTaken`
        """
        for eq in self._eq:
            eq.ProcessDamage(enemy_move)

        # Defend a Type Attack Physical
        if enemy_move.GetTypeAttID() == 1:
            self.__last_dmg_taken = math.floor(enemy_move.RawDmg / (100 + (self.DEF * self._def_buffer)))
            self.HP -= self.LastDamageTaken
        # Defend a Type Attack Magic
        if enemy_move.GetTypeAttID() == 2:
            self.__last_dmg_taken = math.floor(enemy_move.RawDmg / (100 + (self.MDEF * self._def_buffer)))
            self.HP -= self.LastDamageTaken
        # Accumulate HP and Effects
        self.HP = 0 if self.HP < 0 else self.HP
        self.__process_effects(enemy_move._effect_parse)
        enemy_move._effect_parse = {}
        self.Msg = f"{self.name} Dealt {self.LastDamageTaken} dmg."

    def AddCustomMove(self, _move_data: dict):
        """## Parameter
        ------------
        `_move_data`(dict): structured data from `.RPGMovement.move_structure`
        """
        if len(self._custom_moves) >= MAX_OWNED_MOVE:
            return
        self._custom_moves.append(MakeMove(_move_data, owner=self))
        
    def NormalAttack(self, target):
        """## Parameters
        -------------
        `target` (Character): Target Attack.
        """
        return self._normal_move.Use(target)

    def CustomAttack(self, target, option: int):
        """## Parameters
        -------------
        `target` (Character): Target Attack.
        `option` (int): Custom Moves has a list of Moves, option must start from 1 as the first element.
        """
        return self._custom_moves[option - 1].Use(target)

    def __checkPrimSkill(self, skills: dict):
        for n in skills:
            if n == "STR":
                self.RAW_ATT += DATA_LVL[n]['SUM'][skills[n]]
            elif n == "END":
                self.RAW_HP += DATA_LVL[n]['SUM'][skills[n]]
            elif n == "AGI":
                self.RAW_SPD += DATA_LVL[n]['SUM'][skills[n]]
            elif n == "FOC":
                self.RAW_CRIT += DATA_LVL[n]['SUM'][skills[n]]
            elif n == "ITE":
                self.RAW_MATT += DATA_LVL[n]['SUM'][skills[n]]
            elif n == "WIS":
                self.RAW_MDEF += DATA_LVL[n]['SUM'][skills[n]]

    def __checkCharacter(self, type_character: int) -> str:
        """Check the Characteristic of Character, which one is he/she?
        ## Parameter
        ------------
        `type_character` (int): ID of Type Character, It loads from Database
        ## Return
        ---------
        (str): Name of Characteristic
        """
        # Neutral RAW[+HP 10%, -SPD 10%]
        if type_character == 1:
            self.RAW_HP += self.RAW_HP * (10/100)
            self.RAW_SPD -= self.RAW_SPD * (10/100)
            self.__characteristic = "Neutral"
        # Aggresive RAW[+ATT 15% -DEF 15%]
        elif type_character == 2:
            self.RAW_ATT += self.RAW_ATT * (15/100)
            self.RAW_MATT += self.RAW_MATT * (15/100)
            self.RAW_DEF -= self.RAW_DEF * (15/100)
            self.RAW_MDEF -= self.RAW_MDEF * (15/100)
            self.__characteristic = "Aggresive"
        # Careful RAW[+DEF 10% -SPD 10%]
        elif type_character == 3:
            self.RAW_DEF += self.RAW_DEF * (10/100)
            self.RAW_MDEF += self.RAW_MDEF * (10/100)
            self.RAW_SPD -= self.RAW_SPD * (10/100)
            self.__characteristic = "Careful"

    def __process_effects(self, effects):
        pass

class Warrior (Character):

    _att_buffer: float = 1.2
    _def_buffer: float = 1
    _buff_crit: float = 0.8
    _buff_force: float = 1

    def __init__(self, uid: int, name: str, *, _data: dict = None):
        super().__init__(uid, name, _data=_data)
        # Init Attribute
        self.HP = math.ceil(self.RAW_HP * (500/100) / 100)
        self.DEF = math.ceil(self.RAW_DEF * (100/100) / 100)
        self.SPD = math.ceil(self.RAW_SPD * (10/100) / 100)
        self.ATT = math.ceil(self.RAW_ATT * (130/100) / 100)
        self.MIN_ATT = math.ceil(self.ATT * (120/130))
        self.MAX_ATT = math.ceil(self.ATT * (140/130))
        self.CRIT = math.ceil(self.RAW_CRIT * (5/100) / 100)
        self.MANA = math.ceil(self.RAW_MANA * (200/100) / 100)
        self.MATT = math.ceil(self.RAW_MATT * ((175/2) / 100) / 100)
        self.MIN_MATT = math.ceil(self.MATT * (150/175))
        self.MAX_MATT = math.ceil(self.MATT * (200/175))
        self.MATT = math.ceil((self.MIN_MATT + self.MAX_MATT) / 2)
        self.MDEF = math.ceil(self.RAW_MDEF * (100/100) / 100)
        # Set Max Attribute
        self.MAX_HP = self.HP
        self.MAX_DEF = self.DEF
        self.MAX_ATT = self.ATT
        self.MAX_SPD = self.SPD
        self.MAX_CRIT = self.CRIT
        self.MAX_MANA = self.MANA
        self.MAX_MATT = self.MATT
        self.MAX_MDEF = self.MDEF
        # Load Movement
        self._normal_move = MakeMove("Sword Slash", 1, 3, 1, "<me> slashed <enemy> into pieces.", owner=self)
        # Load Equipment
        # Load Item

class Mage (Character):

    _att_buffer: float = 1
    _def_buffer: float = 1.2
    _buff_crit: float = 1
    _buff_force: float = 0.8

    def __init__(self, uid: int, name: str, *, _data: dict = None):
        super().__init__(uid, name, _data=_data)
        # Init Attribute
        self.HP = math.ceil(self.RAW_HP * (500/100) / 100)
        self.DEF = math.ceil(self.RAW_DEF * (100/100) / 100)
        self.SPD = math.ceil(self.RAW_SPD * (8/100) / 100)
        self.ATT = math.ceil(self.RAW_ATT * (50/100) / 100)
        self.MIN_ATT = math.ceil(self.ATT * (40/50))
        self.MAX_ATT = math.ceil(self.ATT * (60/50))
        self.CRIT = math.ceil(self.RAW_CRIT * (10/100) / 100)
        self.MANA = math.ceil(self.RAW_MANA * (400/100) / 100)
        self.MATT = math.ceil(self.RAW_MATT * (170/100) / 100)
        self.MIN_MATT = math.ceil(self.MATT * (160/170))
        self.MAX_MATT = math.ceil(self.RAW_HP * (180/170))
        self.MDEF = math.ceil(self.RAW_MDEF * (100/100) / 100)
        # Set Max Attribute
        self.MAX_HP = self.HP
        self.MAX_DEF = self.DEF
        self.MAX_ATT = self.ATT
        self.MAX_SPD = self.SPD
        self.MAX_CRIT = self.CRIT
        self.MAX_MANA = self.MANA
        self.MAX_MATT = self.MATT
        self.MAX_MDEF = self.MDEF
        # Load Movement
        self._normal_move = MakeMove("Fireball", 2, 1, 1, "<me> cast a Fireball at <enemy>.", owner=self, mana=20)
        # Load Equipment
        # Load Item