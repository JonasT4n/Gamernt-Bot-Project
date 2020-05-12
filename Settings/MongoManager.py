"""

This Script can be Reuseable.

"""

import pymongo
import Settings.botconfig as conf

new_member_data = {
    "member_id": 0,
    "trophy": 0,
    "money": 0,
    "ores": {
        "Copper": 0,
        "Lead": 0,
        "Tin": 0,
        "Coal": 0,
        "Cobalt": 0,
        "Iron": 0,
        "Quartz": 0,
        "Silver": 0,
        "Ruby": 0,
        "Sapphire": 0,
        "Gold": 0,
        "Diamond": 0,
        "Emerald": 0,
        "Titanium": 0,
        "Meteorite": 0
    }
}

class MongoManager:

    connected_collection = None
    database_name: str = None

    def __init__(self, address, dbname):
        """Initialize Connection"""
        try:
            self.client = pymongo.MongoClient(conf.MONGO_ADDRESS)
            self.db = self.client[dbname]
            self.database_name = dbname
        except Exception as e:
            print("Connection Failed. Please Try again Later")
            raise e

    @property
    def dbprop(self):
        """Move to Other Database"""
        return self.db

    @dbprop.setter
    def ChangeDatabase(self, dbname):
        self.db = self.client[dbname]
        self.database_name = dbname

    def ConnectCollection(self, name:str):
        """Connect to a Specific Collection"""
        self.connected_collection = self.db[name]

    def CreateCollection(self, name: str):
        """Create a New Collection"""
        self.db.create_collection(name)
        self.connected_collection = self.db[name]

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
        try:
            self.connected_collection.insert_one(data)
        except:
            print("Error when Inserted, Collection may not defined")

    def UpdateOneObject(self, query: dict, **update):
        """
        
        Update an Object inside Current Connected Collection.

            Parameters :
                query (dict) => A Sample JSON Query to Search a Specific Object Data.
                update (key = value) => The Data you wanted to Update.
            Returns :
                (None)
        
        """
        self.connected_collection.update_one(query, update)

    def DeleteOneObject(self, query: dict):
        """
        
        Delete an Object inside Current Connected Collection.
        
        """
        self.connected_collection.delete_one(query)

    def ClearCollection(self):
        """
        
        Delete All Object or Empty the Collection.
        
        """
        self.connected_collection.delete_many({})

    def FindObject(self, query: dict) -> list:
        """
        
        Find All Objects by Query.
        
        """
        list_objects = [i for i in self.connected_collection.find(query)]
        return list_objects

    def CountObject(self) -> int:
        """
        
        Returns How many Objects inside the Current Selected Collection.
            
            Returns : 
                (int) => Length Of Current2 Collection

        """
        n = len([i for i in self.connected_collection.find({})])
        return n

    def ClearCache(self, collection_name):
        """
        
        Clear Cache in Database to free some Space.
        
        """
        self.db.command({
            "planCacheClear": f"{collection_name}"
        })
        print("Cache Cleared.")
