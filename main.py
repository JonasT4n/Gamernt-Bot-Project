import discord
import os
import asyncio
import datetime
from discord.ext import commands, tasks
import Settings.DbManager as dbm
from itertools import cycle
from webserver import forever

def check_guild_prefix(db: dbm):
    def inner_check(bot, message):
        if not isinstance(message.channel, discord.DMChannel):
            guild = message.guild
            if not db.CheckExistence("guilds", f"id={str(guild.id)}"):
                db.InsertData("guilds", id=guild.id, name=guild.name, created_at=guild.created_at, region=str(guild.region), prefix="g.", last_update_prefix=datetime.datetime.now())
            db.SelectRowData("guilds", f"id={str(guild.id)}")

            n = db.cursor.fetchone()
            if message.content[0:len(n[4])].lower() == n[4].lower():
                return message.content[0:len(n[4])]
            else:
                return "This is Not a Prefix for this Server, Try Again later!..."
        else:
            return 'g.'
    return inner_check

conn = dbm.DbManager.connect_db("./DataPack/guild.db")
bot = commands.Bot(command_prefix=check_guild_prefix(conn))
bot.remove_command("help")

# Attributes
WHITE = 0xfffffe
STATUS = cycle(["Tag Me for Prefix", "Not Game"])

@tasks.loop(seconds=5)
async def change_status():
    await bot.change_presence(activity=discord.Game(name=next(STATUS)))

@bot.event
async def on_ready():
    print("{:^50}\n{:^50}".format("- Bot is Online! -", "|| It's Gamern't Time ||"))
    change_status.start()
    
@bot.event
async def on_member_join(member):
    conn.InsertData("member", server_id=str(member.guild.id), member_id=str(member.id))
    
@bot.event
async def on_member_remove(member):
    conn.DeleteRow("member", server_id=str(member.guild.id), member_id=str(member.id))

@bot.event
async def on_guild_join(guild):
    conn.InsertData("guilds", id=guild.id, name=guild.name, created_at=guild.created_at, region=str(guild.region), prefix="g.", last_update_prefix=datetime.datetime.now())
    for mbr in guild.members:
        if not mbr.bot:
            conn.InsertData("member", server_id=str(guild.id), member_id=str(mbr.id))

@bot.event
async def on_guild_remove(guild):
    conn.DeleteRow("guilds", id=str(guild.id))
    conn.DeleteRow("member", server_id=str(guild.id))

@bot.event
async def on_message(message):
    """Event Message"""
    if not isinstance(message.channel, discord.DMChannel):
        if not conn.CheckExistence("guilds", f"id='{str(message.guild.id)}'"):
            guild = message.guild
            conn.InsertData("guilds", id=guild.id, name=guild.name, created_at=guild.created_at, region=str(guild.region), prefix="g.", last_update_prefix=datetime.datetime.now())

        if not conn.CheckExistence("member", f"server_id={str(message.guild.id)} AND member_id = {str(message.author.id)}") and not message.author.bot:
            conn.InsertData("member", server_id=str(message.guild.id), member_id=str(message.author.id))

        if str(bot.user.id) in message.content: # Get Prefix but tagging Bot
            user_said, in_channel = message.author, message.channel
            this_guild_prefix = conn.cursor.execute("""SELECT prefix FROM guilds WHERE id='{}';""".format(str(message.guild.id)))
            data = this_guild_prefix.fetchone()
            print(data)
            emb = discord.Embed(title=f"Your Server Prefix is {data[0]}\ntype {data[0]}help for commands.", color=discord.Color(WHITE))
            await in_channel.send(embed=emb)

    await bot.process_commands(message)

@bot.command(aliases=['info'])
async def about(ctx):
    """About this Bot"""
    bot_icon = bot.user.avatar_url
    this_guild_prefix = conn.cursor.execute("""SELECT prefix FROM guilds WHERE id={};""".format(str(ctx.message.guild.id)))
    emb = discord.Embed(title="🎮 Gamern't Bot 🎮", description=open("./DataPack/Help/about_desc.txt").read(), colour=discord.Colour(WHITE))
    emb.set_thumbnail(url=bot_icon)
    emb.set_footer(text="Version : 1.0.2b; Your Current Prefix : {}".format(this_guild_prefix.fetchone()[0]))
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
    try:
        if page is None:
            bot_icon = bot.user.avatar_url # https://cdn.discordapp.com/avatars/588179797394456605/1efc5863f4de47420cbdeeabfc13cd2b.webp?size=1024
            emb = discord.Embed(title="🎮 Gamern't Bot - Help", colour=discord.Colour(WHITE))
            emb.add_field(name="1. 📄 General 📄", value="```Common Commands of Gamern't Bot, Absolutely not Game!```", inline=False)
            emb.add_field(name="2. 🎮 Games 🎮", value="```Play Games with others. Good Luck Have Fun!!!```", inline=False)
            emb.add_field(name="3. 😂 Fun 😂", value="```Fun Things to do here.```", inline=False)
            emb.add_field(name="4. ⚙️ Setting ⚙️", value="```May I help you with Settings?```", inline=False)
            emb.add_field(name="5. 🌀 Misc 🌀", value="```Your Personal Inventory will keep your progress Safe, Check it Out!```", inline=False)
            emb.set_thumbnail(url=bot_icon)
            emb.set_footer(text="Example Command : g.help games or g.games")
            await ctx.send(embed=emb)

        elif page.lower() == 'general':
            emb = discord.Embed(colour=discord.Colour(WHITE))
            emb.add_field(name="📄 General Commands 📄", value=open("./DataPack/Help/help.txt", 'r').read(), inline=False)
            emb.set_footer(text="Example Command : g.ping")
            await ctx.send(embed=emb)

        elif page.lower() == 'games':
            emb = discord.Embed(colour=discord.Colour(WHITE))
            emb.add_field(name="🎮 All Games 🎮", value=open("./DataPack/Help/games.txt", 'r').read(), inline=False)
            emb.set_footer(text="Example Command : g.ows how")
            await ctx.send(embed=emb)

        elif page.lower() == 'fun':
            emb = discord.Embed(colour=discord.Colour(WHITE))
            emb.add_field(name="😂 Fun Things 😂", value=open("./DataPack/Help/fun.txt", 'r').read(), inline=False)
            emb.set_footer(text="Example Command : g.duel Trump#0666")
            await ctx.send(embed=emb)

        elif page.lower() == 'setting':
            emb = discord.Embed(colour=discord.Colour(WHITE))
            emb.add_field(name="⚙️ Utility ⚙️", value=open("./DataPack/Help/settings.txt", 'r').read(), inline=False)
            emb.set_footer(text="Example Command : g.giveaway 1000$")
            await ctx.send(embed=emb)

        elif page.lower() == 'misc':
            emb = discord.Embed(colour=discord.Colour(WHITE))
            emb.add_field(name="🌀 Misc 🌀", value=open("./DataPack/Help/misc.txt", 'r').read(), inline=False)
            emb.set_footer(text="Example Command : g.coin")
            await ctx.send(embed=emb)

        else:
            bot_icon = bot.user.avatar_url
            emb = discord.Embed(title="🎮 Gamern't Bot - Help", colour=discord.Colour(WHITE))
            emb.add_field(name="1. 📄 General 📄", value="```Common Commands of Gamern't Bot, Absolutely not Game!```", inline=False)
            emb.add_field(name="2. 🎮 Games 🎮", value="```Play Games with others. Good Luck Have Fun!!!```", inline=False)
            emb.add_field(name="3. 😂 Fun 😂", value="```Fun Things to do here.```", inline=False)
            emb.add_field(name="4. ⚙️ Setting ⚙️", value="```May I help you with Settings?```", inline=False)
            emb.add_field(name="5. 🌀 Misc 🌀", value="```Your Personal Inventory will keep your progress Safe, Check it Out!```", inline=False)
            emb.set_thumbnail(url=bot_icon)
            emb.set_footer(text="Example Command : g.help games")
            await ctx.send(embed=emb)

    except Exception as exc:
        pass

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
        conn.cursor.execute("""UPDATE guilds SET prefix='{}' WHERE id='{}'""".format(new_prefix, str(ctx.message.guild.id)))
        conn.connect.commit()
        emb.add_field(name="🔧 Prefix Changed", value="Server new Prefix **{}**".format(new_prefix))
        await ctx.send(embed=emb)
    except Exception as exc:
        if type(exc) == commands.BadArgument:
            emb.set_footer(text="Example Prefixes : g. | game! | etc.")
            emb.add_field(name="🔧 Not a Good Prefix", value="Your Prefix might too long or bad format, try simpler!")
            await ctx.send(embed=emb)
        print(type(exc), exc)

@bot.command()
async def ping(ctx): # Ping Command, Check Bot Latency
    this_message = await ctx.send("🏓 **Pong! {}ms**".format(int(bot.latency * 1000)))
    also_this_message = ctx.message
    await also_this_message.delete()

@bot.command()
async def general(ctx):
    emb = discord.Embed(colour=discord.Colour(WHITE))
    emb.add_field(name="📄 General Commands 📄", value=open("./DataPack/Help/help.txt", 'r').read(), inline=False)
    emb.set_footer(text="Example Command : g.ping")
    await ctx.send(embed=emb)

@bot.command(aliases=['game'])
async def games(ctx):
    emb = discord.Embed(colour=discord.Colour(WHITE))
    emb.add_field(name="🎮 All Games 🎮", value=open("./DataPack/Help/games.txt", 'r').read(), inline=False)
    emb.set_footer(text="Example Command : g.ows how")
    await ctx.send(embed=emb)
    
@bot.command()
async def fun(ctx):
    emb = discord.Embed(colour=discord.Colour(WHITE))
    emb.add_field(name="😂 Fun Things 😂", value=open("./DataPack/Help/fun.txt", 'r').read(), inline=False)
    emb.set_footer(text="Example Command : g.duel Trump#0666")
    await ctx.send(embed=emb)

@bot.command()
async def setting(ctx):
    emb = discord.Embed(colour=discord.Colour(WHITE))
    emb.add_field(name="⚙️ Setting ⚙️", value=open("./DataPack/Help/settings.txt", 'r').read(), inline=False)
    emb.set_footer(text="Example Command : g.prefix g!")
    await ctx.send(embed=emb)

@bot.command()
async def misc(ctx):
    emb = discord.Embed(colour=discord.Colour(WHITE))
    emb.add_field(name="🌀 Misc 🌀", value=open("./DataPack/Help/misc.txt", 'r').read(), inline=False)
    emb.set_footer(text="Example Command : g.coin")
    await ctx.send(embed=emb)

@bot.command(aliases=['fb', 'report'])
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
    # forever()
    for game in os.listdir("./GamePack"):
        if game.endswith(".py"):
            bot.load_extension("GamePack.{}".format(game[:-3]))
    
    for info in os.listdir("./InformationPack"):
        if info.endswith(".py"):
            bot.load_extension("InformationPack.{}".format(info[:-3]))

    # Run the Bot
    bot.run(os.environ.get("STOKEN"))

    # Bot Stopped Working and Save Data
    conn.connect.commit()
    conn.cursor.close()
    print("{:^50}".format("~ Session Ended, OOF! ~"))