from Settings.MongoManager import MongoManager, new_member_data, new_guild_data

db_for_mbr = MongoManager(collection="members")
db_for_gld = MongoManager(collection="guilds")

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

def checkin_guild(guild_id: int) -> dict:
    """
        
    Check if Guild is in the Database.

        Returns :
            (dict) => Guild Information
    
    """
    query: dict = {"guild_id": str(guild_id)}
    u_data = db_for_gld.FindObject(query)
    if u_data is None:
        gd: dict = new_guild_data
        gd["guild_id"] = str(guild_id)
        db_for_gld.InsertOneObject(gd)
        return gd
    else:
        return u_data[0]

def convert_to_binary_type(filename):
    f = open(filename, 'rb')
    blobData = f.read()
    f.close()
    return blobData