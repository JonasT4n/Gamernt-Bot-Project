"""

This Script can be Reuseable.

"""

import pymongo
from pymongo.errors import *
from Settings.StaticData import DB_NAME, MONGO_ADDRESS

class MongoManager:

    """
    
    Attributes
    ----------
    connect_collection: `MongoClient[DatabaseName][Collection]`
    
    name_database: `DatabaseName`
    
    """

    _connected_collection = None
    _database_name: str = None

    def __init__(self, *, collection: str = None):
        """Initialize Connection"""
        try:
            self.client = pymongo.MongoClient(
                MONGO_ADDRESS,
                connectTimeoutMS = 30000,
                socketTimeoutMS = None
            )
            self.db = self.client[DB_NAME]
            self._database_name = DB_NAME

            if collection is not None:
                self._connected_collection = self.db[collection]

        except Exception as e:
            print("Connection Failed. Please Try again Later")
            raise e

    @property
    def name_database(self):
        return self._database_name

    @name_database.setter
    def name_database(self, dbname: str):
        self.db = self.client[dbname]
        self._database_name = dbname

    @property
    def connect_collection(self):
        return self._connected_collection

    @connect_collection.setter
    def connect_collection(self, collection_name: str):
        self._connected_collection = self.db[collection_name]

    def CreateCollection(self, name: str):
        """Create a New Collection"""
        self.db.create_collection(name)
        self._connected_collection = self.db[name]

    def CheckCollection(self, *args) -> list:
        """
        
        Iterately Check the Collection if it is Exist in Current Database.

            Parameters :
                args (str) => argument of strings
            Returns :
                List of (bool)

        """
        list_collection = self.db.list_collection_names()

        if len(args) == 0:
            print("You Must Insert the Name of Collections into Argument.")
        else:
            list_of_bool: list = []
            for i in args:
                if i in list_collection:
                    list_of_bool.append(True)
                else:
                    list_of_bool.append(False)
            return list_of_bool

    def DropCollection(self, name):
        """Delete Existing Collection"""
        if name in self.CheckCollection(name):
            self.db[name].drop()
        else:
            print("Collection is not in the Database.")
    
    def ListOfCollection(self) -> list:
        """
        
        List of Current Connected Database.
        
        """
        return self.db.list_collection_names()

    def InsertOneObject(self, data: dict):
        """

        Insert a Data to current Connected Collection.

            Parameters :
                data (dict) => A JSON Data
            Returns :
                (None)

        """
        if "_id" in data:
            del data["_id"]
        self._connected_collection.insert_one(data)

    def SetObject(self, query: dict, update: dict, *, usert: bool = False):
        """
        
        Update an Object inside Current Connected Collection.

            Parameters :
                query (dict) => A Sample JSON Query to Search a Specific Object Data.
                update (key = value) => The Data you wanted to Update.
            Returns :
                (None)
        
        """
        self._connected_collection.update_one(query, {"$set": update}, upsert= usert)

    def DeleteOneObject(self, query: dict):
        """
        
        Delete an Object inside Current Connected Collection.

            Parameters :
                query (dict) => Object Selection.
            Returns :
                (None)
        
        """
        self._connected_collection.delete_one(query)

    def UpdateObject(self, query: dict, update: dict, *, usert: bool = False):
        """
        
        Update the Object by Query

            Parameters :
                query (dict) => Object Selection.
                update (dict) => Update the Item or Object.
            Returns :
                (None)

        Reference : https://docs.mongodb.com/manual/reference/operator/
        
        """
        self._connected_collection.update(query, update, upsert=usert)

    def ClearCollection(self):
        """
        
        Delete All Object or Empty the Collection.
        
        """
        self._connected_collection.delete_many({})

    def FindObject(self, query: dict):
        """
        
        Find All Objects by Query.

            Parameters : 
                query (dict) => Find Object Where
            Returns :
                (None) => if no Data
                (list) => if there is
        
        """
        list_objects = [i for i in self._connected_collection.find(query)]
        if len(list_objects) == 0:
            return None
        else:
            return list_objects

    def UnsetItem(self, query: dict, unset: dict, *, usert: bool = False):
        """
        
        Remove an Item inside the Object.

            Parameters :
                query (dict) => Which Object.
                unset (dict) => Item that will be Unset.
            Returns : 
                (None)

        """
        self._connected_collection.update(query, {"$unset": unset}, upsert=usert)

    def IncreaseItem(self, query: dict, inc: dict, *, usert: bool = False):
        """
        
        Remove an Item inside the Object.

            Parameters :
                query (dict) => Which Object.
                inc (dict) => Item that will be Unset.
            Returns : 
                (None)

        """
        self._connected_collection.update(query, {"$inc": inc}, upsert=usert)

    def CountObject(self) -> int:
        """
        
        Returns How many Objects inside the Current Selected Collection.
            
            Returns : 
                (int) => Length Of Current2 Collection

        """
        list_of_collection: list = [i for i in self._connected_collection.find({})]
        n: int = len(list_of_collection)
        return n