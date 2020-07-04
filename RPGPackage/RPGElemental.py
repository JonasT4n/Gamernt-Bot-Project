"""
@Copyright Gamern't RPG 2020
----------------------------
Character Elemental part.
"""

class Elemental:

    """
    Elemental
    ---------
    """

    _typeID: int

    @property
    def ElementType(self):
        return self.__class__.__name__

    @classmethod
    def LoadElement(cls, element_type):
        """
        Load element type. Each element has a unique behaviour.

        Available elements: :class:`Fire`,:class:`Water`, :class:`Earth`, :class:`Air`

        Args:
            `element_type` (str or int): Read element type

        Returns:
            (:class:`Fire` or :class:`Earth` or :class:`Water` or :class:`Air`)
        """
        if isinstance(element_type, int):
            if element_type == 1:
                return Fire()
            elif element_type == 2:
                return Water()
            elif element_type == 3:
                return Earth()
            elif element_type == 4:
                return Air()
        else:
            if element_type.lower() == "fire":
                return Fire()
            elif element_type.lower() == "water":
                return Water()
            elif element_type.lower() == "earth":
                return Earth()
            elif element_type.lower() == "Air":
                return Air()

class Fire(Elemental):

    """
    Fire Elemental
    ----------------
    """

    def __init__(self):
        self._typeID = 1

class Water(Elemental):

    """
    Water Elemental
    ---------------
    """

    def __init__(self):
        self._typeID = 2

class Earth(Elemental):

    """
    Earth Elemental
    ---------------
    """

    def __init__(self):
        self._typeID = 3

class Air(Elemental):

    """
    Air Elemental
    -------------
    """

    def __init__(self):
        self._typeID = 4