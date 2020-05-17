import discord
import os
import asyncio
import datetime
from discord.ext import commands, tasks
from itertools import cycle
from Settings.MongoManager import MongoManager, new_guild_data, new_member_data
from Settings.setting import TOKEN, MONGO_ADDRESS, DB_NAME

def get_prefix(dbm: MongoManager, guild: discord.Guild) -> str:
    guild_data = dbm.FindObject({"guild_id":str(guild.id)})
    if guild_data is None:
        new_gd: dict = new_guild_data
        new_gd["guild_id"] = str(guild.id)
        dbm.InsertOneObject(new_gd)
        return new_gd["prefix"]
    else:
        return guild_data[0]["prefix"]

def set_prefix(dbm: MongoManager, guild: discord.Guild, new_prefix: str):
    dbm.UpdateOneObject({"guild_id":str(guild.id)}, {"prefix":new_prefix})

def check_guild_prefix(dbm: MongoManager):
    def inner_check(bot, message: discord.Message):
        if not isinstance(message.channel, discord.DMChannel):
            guild: discord.Guild = message.guild

            pref: str = get_prefix(dbm, guild)
            if message.content[0:len(pref)].lower() == pref.lower():
                return message.content[0:len(pref)]
            else:
                return "This is Not a Prefix for this Server, Try Again later!..."
        else:
            return 'g.'
    return inner_check

def add_guild(guild_id: int, members: list):
    mdb = MongoManager(MONGO_ADDRESS, DB_NAME)
    mdb.ConnectCollection("guilds")
    query: dict = {"guild_id":str(guild_id)}
    if mdb.FindObject(query) is None:
        return
    else:
        new_gd: dict = new_guild_data
        new_gd["guild_id"] = str(guild_id)
        for mbr in members:
            if not mbr.bot:
                new_gd["members"].append(str(mbr.id))
        mdb.InsertOneObject(new_gd)

def add_member(guild: discord.Guild, member_id: int):
    mdb = MongoManager(MONGO_ADDRESS, DB_NAME)
    mdb.ConnectCollection("guilds")
    query: dict = {"guild_id":str(guild.id)}
    u_data = mdb.FindObject(query)
    if u_data is None:
        add_guild(guild.id, guild.members)
        u_data = mdb.FindObject(query)
    gd: dict = u_data[0]
    gd["members"].append(str(member_id))
    mdb.UpdateOneObject(query, gd)

db = MongoManager(MONGO_ADDRESS, DB_NAME)
db.ConnectCollection("guilds")
bot = commands.Bot(command_prefix=check_guild_prefix(db))
bot.remove_command("help")

# Attributes
WHITE = 0xfffffe
STATUS = cycle(["Tag Me for Prefix", "Not Game"])

# Task Section

@tasks.loop(seconds=5)
async def change_status():
    await bot.change_presence(activity=discord.Game(name=next(STATUS)))

# Events Section

@bot.event
async def on_ready():
    print("{:^50}\n{:^50}".format("- Bot is Online! -", "|| It's Gamern't Time ||"))
    change_status.start()
    
@bot.event
async def on_member_join(member: discord.Member):
    add_member(member.guild, member.id)

@bot.event
async def on_guild_join(guild: discord.Guild):
    add_guild(guild.id, guild.members)

@bot.event
async def on_message(message: discord.Message):
    """Event Message"""
    if not isinstance(message.channel, discord.DMChannel):
        
        if str(bot.user.id) in message.content: # Get Prefix but tagging Bot
            user_said: discord.User = message.author
            in_channel: discord.TextChannel = message.channel
            pref: str = get_prefix(db, message.guild)
            emb = discord.Embed(title=f"Your Server Prefix is {pref}\ntype {pref}help for commands.", color=discord.Color(WHITE))
            await in_channel.send(embed=emb)
    
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    raise error

# Command Section

@bot.command()
async def ping(ctx): # Ping Command, Check Bot Latency
    this_message = await ctx.send("🏓 **Pong! {}ms**".format(int(bot.latency * 1000)))
    also_this_message = ctx.message
    await also_this_message.delete()

@bot.command(aliases=['info'])
async def about(ctx):
    """About this Bot"""
    bot_icon = bot.user.avatar_url
    emb = discord.Embed(
        title="🎮 Gamern't Bot 🎮", 
        description=f"""Hi, I'm not Gamer, i have Good Games to offer and play with you even with your friends, I am Not a Gamer Bot, Trust Me! :D""", 
        colour=discord.Colour(WHITE)
    )
    emb.set_thumbnail(url=bot_icon)
    pref: str = get_prefix(db, ctx.message.guild)
    emb.set_footer(text=f"Version : 1.0.2b; Your Current Prefix : {pref}")
    await ctx.send(embed=emb)
    
@bot.command(aliases=['new'])
async def news(ctx):
    """News about Current Bot Progress"""
    bot_icon = bot.user.avatar_url
    emb = discord.Embed(title="📰 Breaking News!", description=open("./DataPack/Help/news.txt", 'r').read(), colour=discord.Colour(WHITE))
    emb.set_thumbnail(url=bot_icon)
    await ctx.send(embed=emb)

@bot.command(aliases=['h'])
async def help(ctx, page = None):
    """Custom Help Command"""
    emb = discord.Embed(
        title="Help Menu",
        description= open("./DataPack/Help/help_file.txt", "r").read(),
        colour=discord.Colour(WHITE)
    )
    await ctx.send(embed = emb)

@bot.command(aliases=['pfix'])
async def prefix(ctx, new_prefix: str):
    """This Command for Change Server Prefix"""
    this_msg = await ctx.send("Wait for a Moment...")
    await asyncio.sleep(3)
    await this_msg.delete()
    emb = discord.Embed(colour=discord.Colour(WHITE))
    try:
        if len(new_prefix.split(' ')) > 1 or len(new_prefix) > 10 or " " in new_prefix:
            raise commands.BadArgument
        set_prefix(db, ctx.message.guild, new_prefix)
        emb.add_field(name="🔧 Prefix Changed", value="Server new Prefix **{}**".format(new_prefix))
        await ctx.send(embed=emb)
    except commands.BadArgument:
        emb.set_footer(text="Example Prefixes : g. | game! | etc.")
        emb.add_field(name="🔧 Not a Good Prefix", value="Your Prefix might too long or bad format, try simpler!")
        await ctx.send(embed=emb)

@bot.command(aliases=['suggest', 'report'])
async def feedback(ctx, *, args: str):
    """Feedback Report and Bug Glitch Information direct from User"""
    n = open("./report.txt", 'a')
    msg = "\n" + str(datetime.datetime.now()) + f" (By {ctx.message.author.name} : {ctx.message.author.id})" + ": " + args
    n.write(msg)
    n.close()
    await ctx.send("Your Report has been Sent.")

@bot.command()
@commands.is_owner()
async def purge(ctx, limit: int):
    await ctx.channel.purge(limit=limit)

@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    # Shutdown the Bot Application
    await ctx.send("**OOF**")
    await ctx.bot.logout()

@bot.command()
@commands.is_owner()
async def global_info(ctx):
    servers = bot.guilds
    members: int = 0
    for guild in servers:
        members += len(guild.members)
    emb = discord.Embed(title="📈 Stats 📈", colour=discord.Colour(WHITE))
    emb.add_field(name="Server Count", value=f"{len(servers)}")
    emb.add_field(name="Member Count", value=f"{members}")
    await ctx.send(embed = emb)

if __name__ == "__main__":
    # Loading Extensions
    for game in os.listdir("./GamePack"):
        if game.endswith(".py"):
            bot.load_extension("GamePack.{}".format(game[:-3]))

    for info in os.listdir("./InformationPack"):
        if info.endswith(".py"):
            bot.load_extension("InformationPack.{}".format(info[:-3]))

    # Run the Bot
    bot.run(TOKEN)

    # Bot Stopped Working
    print("{:^50}".format("~ Session Ended, OOF! ~"))