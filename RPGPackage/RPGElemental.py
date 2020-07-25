"""
@Copyright Gamern't RPG 2020
----------------------------
Character Elemental part.
"""
TYPE_ELEMENT = {1:"Fire", 2:"Water", 3:"Earth", 4:"Air"}

def checkElement(type_element: int):
    list_element = [Fire(), Water(), Earth(), Air()]
    return list_element[type_element - 1]

class Elemental:
    """
    Elemental
    ---------
    """
    ElementTypeID: int
    ElementEffect: str
    Fumble: dict = {}

    @property
    def ElementType(self):
        return TYPE_ELEMENT[self.ElementTypeID]

class Fire(Elemental):
    """## Fire Elemental
    -----------------
    """
    def __init__(self):
        super().__init__()
        self.ElementTypeID = 1

class Water(Elemental):
    """## Water Elemental
    ------------------
    """
    def __init__(self):
        super().__init__()
        self.ElementTypeID = 2

class Earth(Elemental):
    """## Earth Elemental
    ------------------
    """
    def __init__(self):
        super().__init__()
        self.ElementTypeID = 3

class Air(Elemental):
    """## Air Elemental
    ----------------
    """
    def __init__(self):
        super().__init__()
        self.ElementTypeID = 4