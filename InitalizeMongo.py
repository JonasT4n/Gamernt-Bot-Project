from Settings.MongoManager import MongoManager

mbconn = MongoManager(collection= "members")
gdconn = MongoManager(collection= "guilds")

for i in mbconn.FindObject({}):
    key: str = "member_id"
    mid = i[key]
    if "PRIM-STAT" in i:
        mbconn.SetObject({key: mid}, {
            "moves": {}
        })

# for j in gdconn.FindObject({}):
#     key: str = "guild_id"
#     gid = j[key]