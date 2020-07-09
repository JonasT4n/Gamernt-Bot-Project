from Settings.MongoManager import MongoManager

mbconn = MongoManager(collection="members")
gdconn = MongoManager(collection="guilds")

for i in mbconn.FindObject({}, sortby='backpack.money', limit=5):
    key: str = "member_id"
    mid = i[key]
    print(mid)

# for j in gdconn.FindObject({}):
#     key: str = "guild_id"
#     gid = j[key]
#     gdconn.UnsetItem({key: gid}, {'member': j['member']})