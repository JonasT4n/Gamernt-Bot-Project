from Settings.MongoManager import MongoManager

mbconn = MongoManager(collection= "members")
gdconn = MongoManager(collection= "guilds")

for i in mbconn.FindObject({}):
    member_id = i["member_id"]
    mbconn.SetObject({"member_id": member_id}, {
        "title": "The Man"
    })
    # mbconn.UnsetItem({"member_id": member_id}, {
    #     "type-char": i["type-char"]
    # })

# for j in gdconn.FindObject({}):
#     guild_id = j["guild_id"]
#     gdconn.SetObject({"guild_id": guild_id}, {
#         "MAX-MISC": {
#             "item": 20,
#             "equip": 20,
#             "move": 20
#         }
#     })
#     gdconn.UnsetItem({"guild_id": guild_id}, {
#         "max-misc": {
#             "max-items": j["max-misc"]["max-items"],
#             "max-equip": j["max-misc"]["max-equip"],
#             "max-move": j["max-misc"]["max-move"]
#         },
#         "max-items": 20,
#         "max-equip": 20,
#         "max-move": 20
#     })