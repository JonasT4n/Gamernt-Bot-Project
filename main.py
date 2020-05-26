import discord
import os
import asyncio
import datetime
import shutil
from discord.ext import commands, tasks
from itertools import cycle
from Settings.MyUtility import checkin_member
from Settings.MongoManager import MongoManager, new_guild_data
from Settings.setting import TOKEN

def get_prefix(dbm: MongoManager, guild_id: int) -> str:
    """Get Current Prefix in this Guild."""
    guild_data = dbm.FindObject({"guild_id":str(guild_id)})
    if guild_data is None:
        new_gd: dict = add_guild(dbm, guild_id)
        return new_gd["prefix"]
    else:
        return guild_data[0]["prefix"]

def set_prefix(dbm: MongoManager, guild: discord.Guild, new_prefix: str):
    """Set Guild Prefix and Overwrite to Mongo Data."""
    dbm.UpdateOneObject({"guild_id":str(guild.id)}, {"prefix":new_prefix})

def add_guild(dbmongo: MongoManager, guild_id: int) -> dict:
    """Insert Guild to Mongo Data."""
    gd: dict = new_guild_data
    gd["guild_id"] = str(guild_id)
    dbmongo.InsertOneObject(gd)
    return gd

def add_member_guild(dbm: MongoManager, guild_id: int, member_id: int) -> None:
    """Add Member into Member Guild Array."""
    g_data: dict = get_guild_data(dbm, guild_id)
    member_list: list = g_data["members"]
    member_list.append(str(member_id))
    dbm.UpdateOneObject({"guild_id": str(guild_id)}, {"members": member_list})

def get_guild_data(dbm: MongoManager, guild_id: int) -> dict:
    """Getting a Current Guild Data from Mongo."""
    g_data = dbm.FindObject({"guild_id": str(guild_id)})
    if g_data is None:
        g_data = add_guild(dbm, guild_id)
        return g_data
    else:
        return g_data[0]

def clear_cache_in_folder(path: str):
    for i in os.listdir(path):
        if i == "__pycache__":
            shutil.rmtree(f"{path}/__pycache__")
        if os.path.isdir(f"{path}/{i}"):
            clear_cache(f"{path}/{i}")

def check_guild_prefix(dbm: MongoManager):
    """Check Current Guild Prefix in Command or Message."""
    def inner_check(bot, message: discord.Message):
        if not isinstance(message.channel, discord.DMChannel):
            guild: discord.Guild = message.guild
            pref: str = get_prefix(dbm, guild.id)
            if message.content[0:len(pref)].lower() == pref.lower():
                return message.content[0:len(pref)]
            else:
                return "This is Not a Prefix for this Server, Try Again later!..."
        else:
            return 'g.'
    return inner_check

db_guild = MongoManager(collection="guilds")
bot = commands.Bot(command_prefix=check_guild_prefix(db_guild))
bot.remove_command("help")
current_version: str = "Version 1.0.9b"

# Attributes
WHITE = 0xfffffe
STATUS = cycle(["Tag Me for Prefix", "Not Game"])

# Task Section

@tasks.loop(seconds=5)
async def change_status():
    await bot.change_presence(activity=discord.Game(name=next(STATUS)))

@tasks.loop(hours=1)
async def clear_cache():
    clear_cache_in_folder(".")

# Events Section

@bot.event
async def on_ready():
    print("{:^50}\n{:^50}".format("- Bot is Online! -", "|| It's Gamern't Time ||"))
    change_status.start()
    
@bot.event
async def on_member_join(member: discord.Member):
    add_member_guild(member.guild, member.id)

@bot.event
async def on_guild_join(guild: discord.Guild):
    add_guild(guild.id)

@bot.event
async def on_message(message: discord.Message):
    """Built -in Event Message."""
    # If the Message is not in DM
    if not isinstance(message.channel, discord.DMChannel):

        # Check if Guild not yet in Mongo Data
        gd_data: dict = get_guild_data(db_guild, message.guild.id)
        if str(message.author.id) not in gd_data["members"]:
            add_member_guild(db_guild, message.guild.id, message.author.id)
        
        # Get Prefix by tagging Bot
        if str(bot.user.id) in message.content:
            user_said: discord.User = message.author
            in_channel: discord.TextChannel = message.channel
            pref: str = get_prefix(db_guild, message.guild.id)
            emb = discord.Embed(
                title=f"Your Server Prefix is {pref}\ntype {pref}help for commands.", 
                color=discord.Color(WHITE)
            )
            await in_channel.send(embed=emb)

    # Execute Command No matter what Message Said
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingRequiredArgument):
        return
    if isinstance(error, commands.CommandOnCooldown):
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
    # Initiate Attribute
    bot_icon = bot.user.avatar_url
    pref: str = get_prefix(db_guild, ctx.message.guild)

    # Make Embed and Print Out
    emb = discord.Embed(
        title="🎮 Gamern't Bot 🎮", 
        description=f"""Hi, I'm not Gamer, i have Good Games to offer and play with you even with your friends, I am Not a Gamer Bot, Trust Me! :D\n\nI have been created for those who has bored after playing game, so go to your discord and play with friends while chatting :3""", 
        colour=discord.Colour(WHITE)
    )
    emb.set_thumbnail(url=bot_icon)
    emb.set_footer(text=f"{current_version}\nYour Current Prefix : {pref}")
    await ctx.send(embed=emb)
    
@bot.command(aliases=['new'])
async def news(ctx):
    """News about Current Bot Progress."""
    bot_icon = bot.user.avatar_url
    emb = discord.Embed(title="📰 Breaking News!", description=open("./Help/news.txt", 'r').read(), colour=discord.Colour(WHITE))
    emb.set_thumbnail(url=bot_icon)
    emb.set_footer(text=f"{current_version}")
    await ctx.send(embed=emb)

@bot.command(aliases=['h'])
async def help(ctx, page = None):
    """Custom Help Command."""
    bot_icon_url: str = bot.user.avatar_url
    emb = discord.Embed(
        title="Help Menu",
        description= open("./Help/help_file.txt", "r").read(),
        colour=discord.Colour(WHITE)
    )
    emb.set_thumbnail(url=bot_icon_url)
    emb.set_footer(text=f"{current_version}")
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
        set_prefix(db_guild, ctx.message.guild, new_prefix)
        emb.add_field(name="🔧 Prefix Changed", value="Server new Prefix **{}**".format(new_prefix))
        await ctx.send(embed=emb)
    except commands.BadArgument:
        emb.set_footer(text="Example Prefixes : g. | game! | etc.")
        emb.add_field(name="🔧 Not a Good Prefix", value="Your Prefix might too long or bad format, try simpler!")
        await ctx.send(embed=emb)

@bot.command(aliases=['suggest', 'report'])
async def feedback(ctx: commands.Context, *, args: str):
    """
    
    Feedback Report and Bug Glitch Information direct from User.
    
    """
    mdb = MongoManager(collection="report")
    mdb.UpdateObject({"guild_id": ctx.guild.id}, {"$push": {
        "report": {
            "user": ctx.author.name,
            "id": str(ctx.author.id),
            "said": args,
            "at": str(datetime.datetime.now())
        }
    }})
    await ctx.send("*Your Feedback, Report or Suggestion has been Sent. Thank You :)*")

@bot.command()
@commands.is_owner()
async def purge(ctx, limit: int):
    await ctx.channel.purge(limit=limit)

@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    # Shutdown the Bot Application
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
    emb.add_field(name="Shard Count", value=f"{bot.shard_count}")
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