"""
@Copyright Gamern't RPG 2020
----------------------------
Character Base part.
"""

import math
import random
import discord
from Settings.MyUtility import checkin_member
from RPGPackage.RPGMovement import *

WHITE = 0xfffffe

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

def checkClassID(person: discord.User):
    mbr_data: dict = {}
    if person.bot is False:
        mbr_data = checkin_member(person.id)

    # If Member registered
    if 'CLASSID' in mbr_data:
        # Warrior
        if mbr_data["CLASSID"] == 1:
            return Warrior(person, member_data= mbr_data)

        # Mage
        elif mbr_data["CLASSID"] == 2:
            return Mage(person, member_data= mbr_data)

    # If Member not Registered
    else:
        classes: list = [Warrior(person), Mage(person)]
        this_class = classes[random.randint(0, len(classes) - 1)]
        del classes
        return this_class

class Character:

    # Battle Attribute in Point
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

    # Buff and Fumble
    _att_buffer: float
    _def_buffer: float

    # Misc Attribute
    _last_dmg_taken: int
    # _effects: dict = {}
    _characteristic: str
    _class_name: str
    _msg: str
    # _moves: dict
    _data: dict
    # _item: dict

    _battle_hint: discord.Embed

    @property
    def AttMsg(self):
        return self._msg

    @AttMsg.setter
    def AttMsg(self, msg: str):
        self._msg = msg

    @property
    def LastDamageTaken(self):
        return self._last_dmg_taken

    # @property
    # def Effects(self):
    #     return self._effects
    
    # @Effects.setter
    # def Effects(self, new_effects: dict):
    #     self._effects = new_effects

    # @property
    # def Moves(self):
    #     return self._moves

    # @Moves.setter
    # def Moves(self, moves: dict):
    #     self._moves = moves

    # @property
    # def Items(self):
    #     return self._item

    # @Items.setter
    # def Items(self, items: dict):
    #     self._item = items

    @property
    def GetHint(self):
        return self._battle_hint

    @property
    def ClassName(self):
        return f"{self._characteristic} {self._class_name}"

    @property
    def MemberData(self):
        return self._data

    def checkPrimSkill(self, skills: dict):
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

    def checkCharacter(self, type_character: int) -> str:
        """Check the Characteristic of Character, which one is he/she?

        Args:
            `type_character` (int): ID of Type Character, It loads from Database
            `Character_class` (Character): Assign into the Character

        Returns:
            (str): Name of Characteristic
        """
        char_name: str

        # Neutral RAW[+HP 10%, -SPD 10%]
        if type_character == 1:
            self.RAW_HP += self.RAW_HP * (10/100)
            self.RAW_SPD -= self.RAW_SPD * (10/100)
            char_name = "Neutral"

        # Aggresive RAW[+ATT 15% -DEF 10%]
        elif type_character == 2:
            self.RAW_ATT += self.RAW_ATT * (15/100)
            self.RAW_MATT += self.RAW_MATT * (15/100)
            self.RAW_DEF -= self.RAW_DEF * (10/100)
            self.RAW_MDEF -= self.RAW_MDEF * (10/100)
            char_name = "Aggresive"

        self._characteristic = char_name

    def checkEQ(self, equipment: dict):
        pass

class Warrior (Character):

    _normal_attmsg: str = "ME slash ENEMY through his heart!"

    def __init__(self, person: discord.User, *, member_data: dict = None):
        self.person = person
        self.id = person.id
        self.name = person.name
        self._data = member_data

        # Get Characteristic
        if member_data is not None:
            self.checkCharacter(member_data['CHARID'])
            self.checkPrimSkill(member_data['PRIM-STAT'])
            self.Moves = member_data['moves']
            self.Items = member_data['backpack']['item']
            self._battle_hint = discord.Embed(
                title= f"🎬 {self.name}'s Moves, ACTION!",
                description= "How to Play?\n"
                    f"> Send `use normal <target>` in channel to use normal attack from your class.\n"
                    f"> Send `use <move> <target>` in channel to use one of your custom move.\n"
                    f"> Send `use <item> <target>` in channel to use your battle item from inventory.\n"
                    "Your Normal Attack as Warrior :\n"
                    "```| Sword Slash |\n"
                    "Type: Weapon\n"
                    "Elemental: Earth\n"
                    "Attack: Single\n"
                    "MSG: ME slash ENEMY through his heart!```",
                colour= discord.Colour(WHITE)
                )
            for move in range(len(self.Moves)):
                self._battle_hint.add_field(
                    name= self.Moves[self.Moves[move]]['name'],
                    value= self.Moves[self.Moves[move]]['desc'],
                    inline= False
                    )
        else:
            self._battle_hint = discord.Embed(
                title= f"🎬 {self.name}'s Moves, ACTION!",
                description= "`You are currently unregistered which you can only use normal move.`\nHow to Play?\n"
                    f"> Send `use normal <target>` in channel to use normal attack from your class.\n"
                    f"> Send `use <move> <target>` in channel to use one of your custom move.\n"
                    f"> Send `use <item> <target>` in channel to use your battle item from inventory.\n"
                    "Your Normal Attack as Warrior :\n"
                    "```| Sword Slash |\n"
                    "Type: Weapon\n"
                    "Elemental: Earth\n"
                    "Attack: Single\n"
                    "MSG: ME slash ENEMY through his heart!```",
                colour= discord.Colour(WHITE)
                )
            self.checkCharacter(random.randint(1, 2))

        # Init Attribute
        self.HP = math.ceil(self.RAW_HP * (800/100) / 100)
        self.DEF = math.ceil(self.RAW_DEF * (100/100) / 100)
        self.SPD = math.ceil(self.RAW_SPD * (10/100) / 100)
        self.ATT = math.ceil(self.RAW_ATT * (130/100) / 100)
        self.MIN_ATT = math.ceil(self.ATT * (120/130))
        self.MAX_ATT = math.ceil(self.ATT * (140/130))
        self.CRIT = math.ceil(self.RAW_CRIT * (5/100) / 100)
        self.MANA = math.ceil(self.RAW_MANA * (400/100) / 100)
        self.MATT = math.ceil(self.RAW_MATT * ((175/2) / 100) / 100)
        self.MIN_MATT = math.ceil(self.MATT * (150/175))
        self.MAX_MATT = math.ceil(self.MATT * (200/175))
        self.MATT = math.ceil((self.MIN_MATT + self.MAX_MATT) / 2)
        self.MDEF = math.ceil(self.RAW_MDEF * (100/100) / 100)

        self._class_name = "Warrior"
        self._att_buffer = 1.2
        self._def_buffer = 1

        # Set Max Attribute
        self.MAX_HP = self.HP
        self.MAX_DEF = self.DEF
        self.MAX_ATT = self.ATT
        self.MAX_SPD = self.SPD
        self.MAX_CRIT = self.CRIT
        self.MAX_MANA = self.MANA
        self.MAX_MATT = self.MATT
        self.MAX_MDEF = self.MDEF

    def NormalAttack(self):
        """
        Normal Attack : Sword Slash (Weapon)
        
        Returns:
            `Index 0` (int): ID of Type Attack
            `Index 1` (int): Raw Damage

        """
        buffer: float = self._att_buffer
        if random.randint(1, 100) < self.CRIT:
            buffer += 0.8
        self.AttMsg = self._normal_attmsg
        return 1, random.randint(self.MIN_ATT, self.MAX_ATT) * buffer

    def Defend(self, attack_type: int, raw_dmg: int):
        """
        Defend Against the Attack

        Returns:
            (int): Damage that has been Takens

        Note: You can get this Info from method `LastDamageTaken`
        """
        # Defend against Weapon Attack
        buffer: float = self._def_buffer
        if attack_type == 1:
            self._last_dmg_taken = math.ceil((raw_dmg*100) / (100+(self.DEF*buffer)))
            self.HP -= self._last_dmg_taken

        # Defend against Magic Attack
        elif attack_type == 2:
            self._last_dmg_taken = math.ceil((raw_dmg*100) / (100+(self.MDEF*buffer)))
            self.HP -= self._last_dmg_taken

        self._msg = f"Dealt **{self._last_dmg_taken}** dmg"
        return self._last_dmg_taken

class Mage (Character):

    _normal_attmsg: str = "ME uses Fireball, tryna burn ENEMY."

    def __init__(self, person: discord.User, *, member_data: dict = None):
        self.person = person
        self.id = person.id
        self.name = person.name
        self._data = member_data

        # Get Characteristic
        if member_data is not None:
            self.checkCharacter(member_data['CHARID'])
            self.checkPrimSkill(member_data['PRIM-STAT'])
            self.Moves = member_data['moves']
            self.Items = member_data['backpack']['item']
            self._battle_hint = discord.Embed(
                title= f"🎬 {self.name}'s Moves, ACTION!",
                description= "How to Play?\n"
                    f"> Send `use normal <target>` in channel to use normal attack from your class.\n"
                    f"> Send `use <move> <target>` in channel to use one of your custom move.\n"
                    f"> Send `use <item> <target>` in channel to use your battle item from inventory.\n"
                    "Your Normal Attack as Mage :\n"
                    "```| Fireball |\n"
                    "Type: Magic\n"
                    "Elemental: Fire\n"
                    "Attack: Single\n"
                    "Mana Cost : 30\n"
                    "MSG: ME uses Fireball, tryna burn ENEMY.```",
                colour= discord.Colour(WHITE)
                )
            for move in range(len(self.Moves)):
                self._battle_hint.add_field(
                    name= self.Moves[self.Moves[move]]['name'],
                    value= self.Moves[self.Moves[move]]['desc'],
                    inline= False
                    )
        else:
            self._battle_hint = discord.Embed(
                title= f"🎬 {self.name}'s Moves, ACTION!",
                description= "`You are currently unregistered which you can only use normal move.`\nHow to Play?\n"
                    f"> Send `use normal <target>` in channel to use normal attack from your class.\n"
                    "Your Normal Attack as Mage :\n"
                    "```| Fireball |\n"
                    "Type: Magic\n"
                    "Elemental: Fire\n"
                    "Attack: Single\n"
                    "Mana Cost : 30\n"
                    "MSG: ME uses Fireball, tryna burn ENEMY.```",
                colour= discord.Colour(WHITE)
                )
            self.checkCharacter(random.randint(1, 2))

        # Init Attribute
        self.HP = math.ceil(self.RAW_HP * (800/100) / 100)
        self.DEF = math.ceil(self.RAW_DEF * (100/100) / 100)
        self.SPD = math.ceil(self.RAW_SPD * (8/100) / 100)
        self.ATT = math.ceil(self.RAW_ATT * (50/100) / 100)
        self.MIN_ATT = math.ceil(self.ATT * (40/50))
        self.MAX_ATT = math.ceil(self.ATT * (60/50))
        self.CRIT = math.ceil(self.RAW_CRIT * (10/100) / 100)
        self.MANA = math.ceil(self.RAW_MANA * (650/100) / 100)
        self.MATT = math.ceil(self.RAW_MATT * (170/100) / 100)
        self.MIN_MATT = math.ceil(self.MATT * (160/170))
        self.MAX_MATT = math.ceil(self.RAW_HP * (180/170))
        self.MDEF = math.ceil(self.RAW_MDEF * (100/100) / 100)

        self._class_name = "Mage"
        self._att_buffer = 1
        self._def_buffer = 1.2

        # Set Max Attribute
        self.MAX_HP = self.HP
        self.MAX_DEF = self.DEF
        self.MAX_ATT = self.ATT
        self.MAX_SPD = self.SPD
        self.MAX_CRIT = self.CRIT
        self.MAX_MANA = self.MANA
        self.MAX_MATT = self.MATT
        self.MAX_MDEF = self.MDEF

    def NormalAttack(self):
        """
        Normal Attack : Fireball (Magic)

        Returns:
            `Index 0` (int): ID of Type Attack
            `Index 1` (int): Raw Damage
        """
        buffer: float = self._att_buffer
        if random.randint(1, 100) < self.CRIT:
            buffer += 1
        self.MANA -= 30
        self.AttMsg = self._normal_attmsg
        return 2, random.randint(self.MIN_MATT, self.MAX_MATT) * buffer

    def Defend(self, attack_type: int, raw_dmg: int):
        """
        Defend Against the Attack

        Returns:
            (int): Damage that has been Takens

        Note: You can get this Info from method `LastDamageTaken`
        """
        # Defend against Weapon Attack
        buffer: float = self._def_buffer
        if attack_type == 1:
            self._last_dmg_taken = math.ceil((raw_dmg*100) / (100+(self.DEF*buffer)))
            self.HP -= self._last_dmg_taken

        # Defend against Magic Attack
        elif attack_type == 2:
            self._last_dmg_taken = math.ceil((raw_dmg*100) / (100+(self.MDEF*buffer)))
            self.HP -= self._last_dmg_taken

        return self._last_dmg_taken
