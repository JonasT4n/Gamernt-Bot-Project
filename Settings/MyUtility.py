from Settings.MongoManager import MongoManager, new_member_data
from Settings.setting import MONGO_ADDRESS, DB_NAME

db_for_mbr = MongoManager(MONGO_ADDRESS, DB_NAME)
db_for_mbr.ConnectCollection("members")

db_for_gld = MongoManager(MONGO_ADDRESS, DB_NAME)
db_for_gld.ConnectCollection("guilds")

def checkin_member(member_id: int) -> dict:
    """
        
    Check if Member is in the Database.

        Returns :
            (dict) => Member Information
    
    """
    query: dict = {"member_id":str(member_id)}
    u_data = db_for_mbr.FindObject(query)
    if u_data is None:
        nd: dict = new_member_data
        nd["member_id"] = str(member_id)
        db_for_mbr.InsertOneObject(nd)
        return nd
    else:
        return u_data[0]

def convert_to_binary_type(filename):
    f = open(filename, 'rb')
    blobData = f.read()
    f.close()
    return blobData