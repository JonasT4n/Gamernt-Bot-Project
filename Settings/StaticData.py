import os

try:
    TOKEN = os.environ['STOKEN']
    MONGO_ADDRESS = os.environ.get("MONGO_ADDRESS")
    DB_NAME = os.environ.get("DB_NAME")
    GOOGLE_API = os.environ.get("GOOGLE_API")
    CSE_ID = os.environ.get("CSE_ID")
except KeyError:
    from bin_folder.secret import a, b, c, d, e
    TOKEN = a
    MONGO_ADDRESS = b
    DB_NAME = c
    GOOGLE_API = d
    CSE_ID = e

# Database Attribute
new_guild_data: dict = {
    "guild_id": "0",
    "prefix": "g.",
    "stories": [],
    "currency": {
        "chat-min": 5,
        "chat-max": 10,
        "type": "💸",
        "last-modified": None,
        "modif-by": None 
    },
    "max-misc": {
        "max-items": 20,
        "max-equip": 20,
        "max-move": 20
    },
    "shop": {
        "items": {},
        "equipments": {},
        "movement": {}
    }
}
new_member_data: dict = {
    "member_id": None,
    "title": "The Man",
    "backpack": {
        "pickaxe-level": 0,
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
        },
        "money": {}
    }
}
start_rpg: dict = {
    "CHARID": 1,
    "CLASSID": 1,
    "TRP": 0,
    "LVL": 0,
    "EXP": 0,
    "win-count": 0,
    "lost-count": 0,
    "skill-point": 0,
    "equip": {},
    "MAX-ITEM-HOLD": 10,
    "backpack.item": {},
    "PRIM-STAT": {
        "STR": 0,
        "END": 0,
        "AGI": 0,
        "FOC": 0,
        "ITE": 0,
        "WIS": 0
    },
    "moves": {}
}

# Pickaxe Identity
pickaxe_identity: dict = {
    0: {
        "requirement": None,
        "balance": {
            "Copper": 2500,
            "Lead": 1200,
            "Tin": 800,
            "Coal": 500,
            "Iron": 300,
            "Cobalt": 250,
            "Quartz": 200,
            "Silver": 120,
            "Gold": 100,
            "Sapphire": 85,
            "Ruby": 75,
            "Diamond": 30,
            "Emerald": 20,
            "Titanium": 10,
            "Meteorite": 5
        }
    },
    1: {
        "requirement": {
            "Copper": 12,
            "Lead": 8,
            "Tin": 6,
            "Iron": 3,
            "Cobalt": 1,
            "Silver": 1
        },
        "balance": {
            "Copper": 3000,
            "Lead": 1500,
            "Tin": 1000,
            "Coal": 650,
            "Iron": 450,
            "Cobalt": 350,
            "Quartz": 250,
            "Silver": 145,
            "Gold": 105,
            "Sapphire": 90,
            "Ruby": 80,
            "Diamond": 30,
            "Emerald": 20,
            "Titanium": 10,
            "Meteorite": 6
        }
    },
    2: {
        "requirement": {
            "Copper": 12,
            "Lead": 25,
            "Coal": 12,
            "Iron": 5,
            "Silver": 5,
            "Quartz": 2
        },
        "balance": {
            "Copper": 3500,
            "Lead": 1750,
            "Tin": 1500,
            "Coal": 800,
            "Iron": 500,
            "Cobalt": 350,
            "Quartz": 300,
            "Silver": 175,
            "Gold": 125,
            "Sapphire": 100,
            "Ruby": 90,
            "Diamond": 35,
            "Emerald": 30,
            "Titanium": 18,
            "Meteorite": 8
        }
    },
    3: {
        "requirement": {
            "Copper" : 25,
            "Lead": 15,
            "Tin": 20,
            "Iron": 12,
            "Quartz": 6,
            "Gold": 3
        },
        "balance": {
            "Copper": 3750,
            "Lead": 2200,
            "Tin": 1800,
            "Coal": 1000,
            "Iron": 800,
            "Cobalt": 500,
            "Quartz": 450,
            "Silver": 305,
            "Gold": 245,
            "Sapphire": 120,
            "Ruby": 120,
            "Diamond": 50,
            "Emerald": 35,
            "Titanium": 25,
            "Meteorite": 10
        }
    },
    4: {
        "requirement": {
            "Copper": 50,
            "Tin": 10,
            "Iron": 10,
            "Quartz": 5,
            "Gold": 5,
            "Titanium": 1
        },
        "balance": {
            "Copper": 4000,
            "Lead": 2500,
            "Tin": 2000,
            "Coal": 1200,
            "Iron": 1000,
            "Cobalt": 550,
            "Quartz": 500,
            "Silver": 350,
            "Gold": 250,
            "Sapphire": 150,
            "Ruby": 150,
            "Diamond": 60,
            "Emerald": 40,
            "Titanium": 30,
            "Meteorite": 12
        }
    },
    5: {
        "requirement": None,
        "balance": {
            "Copper": 4000,
            "Lead": 2500,
            "Tin": 2000,
            "Coal": 1200,
            "Iron": 1000,
            "Cobalt": 550,
            "Quartz": 500,
            "Silver": 350,
            "Gold": 250,
            "Sapphire": 150,
            "Ruby": 150,
            "Diamond": 60,
            "Emerald": 40,
            "Titanium": 30,
            "Meteorite": 12
        }
    }
}

# Words
words: dict = {
    "Country":
    [
        'Afghanistan', 'Albania', 'Algeria', 'Andorra', 'Angola', 'Antigua', 'Barbuda', 'Argentina', 'Armenia', 'Australia', 'Austria', 'Azerbaijan', 'Bahamas', 'Bahrain', 
        'Bangladesh', 'Barbados', 'Belarus', 'Belgium', 'Belize', 'Benin', 'Bhutan', 'Bolivia', 'Bosnia', 'Herzegovina', 'Botswana', 'Brazil', 'Brunei Darussalam', 
        'Bulgaria', 'Burkina Faso', 'Burundi', 'Cabo Verde', 'Cambodia', 'Cameroon', 'Canada', 'Central African Republic', 'Chad', 'Chile', 'China', 'Colombia', 
        'Comoros', 'Congo', 'Cook Islands', 'Costa Rica', 'Croatia', 'Cuba', 'Cyprus', 'Czechia', "Cote d'Ivoire",'Congo', 'Denmark', 'Djibouti', 'Dominica', 
        'Dominican Republic', 'Ecuador', 'Egypt', 'El Salvador', 'Equatorial Guinea', 'Eritrea', 'Estonia', 'Eswatini', 'Ethiopia', 'Faroe Islands', 'Fiji', 
        'Finland', 'France', 'Gabon', 'Gambia', 'Georgia', 'Germany', 'Ghana', 'Greece', 'Grenada', 'Guatemala', 'Guinea', 'Guinea Bissau', 'Guyana', 'Haiti', 
        'Honduras', 'Hungary', 'Iceland', 'India', 'Indonesia', 'Iran', 'Iraq', 'Ireland', 'Israel', 'Italy', 'Jamaica', 'Japan', 'Jordan', 'Kazakhstan', 'Kenya', 
        'Kiribati', 'Kuwait', 'Kyrgyzstan', "Laos", 'Latvia', 'Lebanon', 'Lesotho', 'Liberia', 'Libya', 'Lithuania', 'Luxembourg', 'Madagascar', 'Malawi', 'Malaysia', 
        'Maldives', 'Mali', 'Malta', 'Marshall Islands', 'Mauritania', 'Mauritius', 'Mexico', 'Micronesia', 'Monaco', 'Mongolia', 'Montenegro', 'Morocco', 'Mozambique', 
        'Myanmar', 'Namibia', 'Nauru', 'Nepal', 'Netherlands', 'New Zealand', 'Nicaragua', 'Niger', 'Nigeria', 'Niue', 'North Macedonia', 'Norway', 'Oman', 'Pakistan', 
        'Palau', 'Panama', 'Papua New Guinea', 'Paraguay', 'Peru', 'Philippines', 'Poland', 'Portugal', 'Qatar', 'South Korea', 'North Korea', 'Moldova', 'Romania', 
        'Russia', 'Rwanda', 'Saint Kitts and Nevis', 'Saint Lucia', 'Samoa', 'San Marino', 'Saudi Arabia', 'Senegal', 'Serbia', 'Seychelles', 'Sierra Leone', 'Singapore', 
        'Slovakia', 'Slovenia', 'Solomon Islands', 'Somalia', 'South Africa', 'South Sudan', 'Spain', 'Sri Lanka', 'Sudan', 'Suriname', 'Sweden', 'Switzerland', 'Syria', 
        'Tajikistan', 'Thailand', 'Timor-Leste', 'Togo', 'Tokelau ', 'Tonga', 'Trinidad', 'Tobago', 'Tunisia', 'Turkey', 'Turkmenistan', 'Tuvalu', 'Uganda', 'Ukraine', 
        'United Arab Emirates', 'United Kingdom', 'Great Britain', 'Tanzania', 'United States America', 'Uruguay', 'Uzbekistan', 'Vanuatu', 'Venezuela', 'VietNam', 'Yemen', 
        'Zambia'
    ],
    "Fruit":
    [
        'Apple', 'Apricots', 'Avocado', 'Banana', 'Blackberries', 'Blackcurrant', 'Blueberries', 'Breadfruit', 'Cantaloupe', 'Carambola', 'Cherimoya', 
        'Cherries', 'Clementine', 'Coconut', 'Cranberries', 'Custard Apple', 'Date Fruit', 'Dragonfruit', 'Durian', 'Elderberries', 'Feijoa', 'Figs', 
        'Gooseberries', 'Grapefruit', 'Grapes', 'Guava', 'Honeydew Melon', 'Jackfruit', 'Java Plum', 'Jujube Fruit', 'Kiwifruit', 'Kumquat', 'Lemon', 
        'Lime', 'Longan', 'Loquat', 'Lychee', 'Mandarin', 'Mango', 'Mangosteen', 'Mulberries', 'Nectarine', 'Olives', 'Orange', 'Papaya', 'Passion Fruit', 
        'Peaches', 'Pear', 'Pineapple', 'Pitanga', 'Plantain', 'Plums', 'Pomegranate', 'Prickly Pear', 'Prunes', 'Pummelo', 'Quince', 'Raspberries', 
        'Rhubarb', 'Rose Apple', 'Sapodilla', 'Sapote Mamey', 'Soursop', 'Strawberries', 'Sugar Apple', 'Tamarind', 'Tangerine', 'Watermelon'
    ],
    'Animal':
    [
        'Albatross', 'Alligator', 'Arctic-Wolf', 'Badger', 'Bat', 'Bear', 'Bee', 'Blue-whale', 'Camel', 'Cat', 'Chicken', 'Chimpanzee', 'Cow', 
        'Coyote', 'Crab', 'Crocodile', 'Crow', 'Deer', 'Dog', 'Dolphin', 'Dove', 'Ducks', 'Eagle', 'Elephant', 'Elk', 'Fish', 'Flamingo', 'Fox', 
        'Frog', 'Giraffe', 'Goat', 'Goldfish', 'Goose', 'Gorilla', 'Hamster', 'Hare', 'Hawk', 'Hedgehog', 'Hedgehong', 'Hippopotamus', 'Horse', 
        'Hummingbird', 'Kangaroo', 'Kitten', 'Koala', 'Leopard', 'Lion', 'Lizard', 'Mole', 'Monkey', 'Mouse', 'Ostrich', 'Otter', 'Owl', 'Ox', 
        'Panda', 'Parrot', 'Peacock', 'Penguin', 'Pig', 'Pigeon', 'Puppy', 'Rabbit', 'Raccoon', 'Rat', 'Raven', 'Reindeer', 'Robin', 'Seagull', 
        'Sheep', 'Shrimp', 'Snake', 'Sparrow', 'Squirrel', 'Starfish', 'Stork', 'Swallow', 'Swan', 'Tiger', 'Toad', 'Turkey', 'Turtle', 'Vulture', 
        'Walrus', 'Woodpecker'
    ],
    'Videogame':
    [
        'Assassins Creed', 'Asteroids', 'BioShock', 'Bloodborne', 'Brawl Stars', 'Brawlhalla', 'Call of Duty', 'Castlevania', 'Chrono Trigger', 'Civilization', 
        'Clash Royale', 'Clash of Clan', 'Cuphead', 'Dark Souls', 'Dead Space', 'Diablo', 'Donkey Kong', 'Doom', 'Dota', 'Double Dragon', 'Dungeon Master', 
        'Fallout', 'Final Fantasy', 'Fire Emblem', 'Fortnite', 'Forza Horizon', 'Gears of War', 'God of War', 'Gone Home', 'Grand Theft Auto', 'Grim Fandango', 
        'Guitar Hero', 'Half Life', 'Halo Combat Evolved', 'Hay Day', 'Journey', 'Kingdom Hearts', 'Last Day on Earth', 'League of Legends', 'Left Four Dead', 
        'Legend of Zelda', 'Limbo', 'Mario Kart', 'Mass Effect', 'Mega Man', 'Metal Gear Solid', 'Minecraft', 'Monopoly', 'Mortal Combat', 'Myst', 'The Oregon Trail', 
        'Overwatch', 'Pac Man', 'Paladin', 'Pokemon', 'Portal', 'Resident Evil', 'Rocket League', 'Secret of Mana', 'Shadow of the Colossus', 'Silent Hill', 'SimCity', 
        'Skyrim', 'Sonic the Hedgehog', 'Soulcalibur', 'Spelunky', 'StarCraft', 'Stardew Valley', 'Street Fighter', 'Super Mario Bros', 'Super Mario Odyssey', 
        'Super Metroid', 'Super Smash Bros', 'Tecmo Super Bowl', 'Tekken', 'Tetris', 'The Last of Us', 'The Sims', 'The Witcher', 'Timesplitters', 'Tomb Raider', 
        'Twisted Metal', 'Uncharted', 'Undertale', 'Wii Sports', 'World of Warcraft', 'Geometry Dash', 'Piano Tiles', 'OSU', 'Ori and The Will of The Wisps', 'Contra',
        'Ori and The Blind Forest', 'Team Fortress', 'Candy Crush Saga', 'Public Unknown Battlegrounds', 'Mortal Kombat', 'Life is Strange', 'Devil May Cry', 'Super Mario Maker',
        'The Outer Worlds', 'Death Stranding', 'Apex Legends', 'Bomberman', 'Street Fighter', 'Dynasty Warriors', 'Angry Birds', 'Gran Turismo', 'Pong', 'Red Dead Redemption',
        'Wolfenstein', 'StarCraft', 'Zork', 'Space Invaders', 'Counter Strike', 'Quake', ''
    ]
}

# Card Game Cards
card_deck_dict: dict = {
    "spade":["A♤", "2♤", "3♤", "4♤", "5♤", "6♤", "7♤", "8♤", "9♤", "10♤", "J♤", "Q♤", "K♤"],
    "heart":["A♡", "2♡", "3♡", "4♡", "5♡", "6♡", "7♡", "8♡", "9♡", "10♡", "J♡", "Q♡", "K♡"],
    "club":["A♧", "2♧", "3♧", "4♧", "5♧", "6♧", "7♧", "8♧", "9♧", "10♧", "J♧", "Q♧", "K♧"],
    "diamond":["A♢", "2♢", "3♢", "4♢", "5♢", "6♢", "7♢", "8♢", "9♢", "10♢", "J♢", "Q♢", "K♢"]
}

card_deck_list: list = [
    "A♤", "2♤", "3♤", "4♤", "5♤", "6♤", "7♤", "8♤", "9♤", "10♤", "J♤", "Q♤", "K♤", 
    "A♡", "2♡", "3♡", "4♡", "5♡", "6♡", "7♡", "8♡", "9♡", "10♡", "J♡", "Q♡", "K♡", 
    "A♧", "2♧", "3♧", "4♧", "5♧", "6♧", "7♧", "8♧", "9♧", "10♧", "J♧", "Q♧", "K♧",
    "A♢", "2♢", "3♢", "4♢", "5♢", "6♢", "7♢", "8♢", "9♢", "10♢", "J♢", "Q♢", "K♢"
]