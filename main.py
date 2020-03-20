import discord
from discord.ext import commands, tasks
import Settings.Handler as handle
import Settings.DbManager as database
import os, asyncio, time, random
from Settings.webserver import run_web

conn = database.DbManager.connect_db("./DataPack/guild.db")
bot = commands.Bot(command_prefix=handle.check_guild_prefix(conn))
bot.remove_command("help")
WHITE = 0xfffffe

@bot.event
async def on_ready():
    print("{:^50}\n{:^50}".format("- Bot is Online! -", "|| It's Gamern't Time ||"))
    await bot.change_presence(activity=discord.Game("Absolutely Not Game"))
    
@bot.event
async def on_member_join(member):
    temp = database.DbManager.connect_db("./DataPack/member.db")
    temp.cursor.execute("""SELECT * FROM point WHERE id=:id""", {"id":str(member.id)})
    ex = temp.cursor.fetchone()
    if ex is None:
        temp.cursor.execute("""INSERT INTO point VALUES (:id, :zero)""", {"id":str(member.id), "zero":0})
        temp.connect.commit()
    temp.cursor.close()

@bot.event
async def on_guild_join(guild):
    temp = database.DbManager.connect_db("./DataPack/member.db")
    conn.InsertData("guilds", id=guild.id, name=guild.name, created_at=guild.created_at, region=str(guild.region), prefix="g.")
    for member in guild.members:
        if not member.bot:
            temp.cursor.execute("""SELECT * FROM point WHERE id=:id""", {"id":str(member.id)})
            ex = temp.cursor.fetchone()
            if ex is None:
                temp.cursor.execute("""INSERT INTO point VALUES (:id, :zero)""", {"id":str(member.id), "zero":0})
            else:
                continue
    temp.connect.commit()
    temp.cursor.close()

@bot.event
async def on_message(message):
    """Event Message"""
    if message.content == bot.user.mention:
        user_said, in_channel = message.author, message.channel
        this_guild_prefix = conn.cursor.execute("""SELECT prefix FROM guilds WHERE id={};""".format(str(message.guild.id)))
        emb = discord.Embed(title="Your Server Prefix is {}".format(this_guild_prefix.fetchone()[0]), color=discord.Color(WHITE))
        await message.delete()
        await in_channel.send(embed=emb)
    await bot.process_commands(message)

@bot.command(aliases=['a'])
async def about(ctx):
    """About this Bot"""
    bot_icon = bot.user.avatar_url
    this_guild_prefix = conn.cursor.execute("""SELECT prefix FROM guilds WHERE id={};""".format(str(ctx.message.guild.id)))
    emb = discord.Embed(title="🎮 Gamern't Bot 🎮", description="Contains Good Games, This is Not a Game Bot, Trust Me!", colour=discord.Colour(WHITE))
    emb.set_thumbnail(url=bot_icon)
    emb.set_footer(text="Version : 1.0.1; Your Current Prefix : {}".format(this_guild_prefix.fetchone()[0]))
    await ctx.send(embed=emb)
    
@bot.command(aliases=['new'])
async def news(ctx):
    """News about Current Bot Progress"""
    bot_icon = bot.user.avatar_url
    emb = discord.Embed(title="📰 Breaking News!", description="- Uno Commands Currently Disabled due to Buggy Gameplay.")
    emb.set_thumbnail(bot_icon)
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
            emb.add_field(name="4. ⚙️ Util ⚙️", value="```Bot will serve you.```", inline=False)
            emb.set_thumbnail(url=bot_icon)
            emb.set_footer(text="Example Command : g.help games")
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
        elif page.lower() == 'util':
            emb = discord.Embed(colour=discord.Colour(WHITE))
            emb.add_field(name="⚙️ Utility ⚙️", value=open("./DataPack/Help/utility.txt", 'r').read(), inline=False)
            emb.set_footer(text="Example Command : g.giveaway 1000$")
            await ctx.send(embed=emb)
        else:
            bot_icon = bot.user.avatar_url
            emb = discord.Embed(title="🎮 Gamern't Bot - Help", colour=discord.Colour(WHITE))
            emb.add_field(name="1. 📄 General 📄", value="```Common Commands of Gamern't Bot, Absolutely not Game!```", inline=False)
            emb.add_field(name="2. 🎮 Games 🎮", value="```Play Games with others. Good Luck Have Fun!!!```", inline=False)
            emb.add_field(name="3. 😂 Fun 😂", value="```Fun Things to do here.```", inline=False)
            emb.add_field(name="4. ⚙️ Util ⚙️", value="```Bot will serve you.```", inline=False)
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
async def util(ctx):
    emb = discord.Embed(colour=discord.Colour(WHITE))
    emb.add_field(name="⚙️ Utility ⚙️", value=open("./DataPack/Help/utility.txt", 'r').read(), inline=False)
    emb.set_footer(text="Example Command : g.giveaway 1000$")
    await ctx.send(embed=emb)

@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    await ctx.send("**OOF**")
    await ctx.bot.logout()

if __name__ == '__main__':
    run_web()
    for game in os.listdir("./GamePack"):
        if game.endswith(".py"):
            if "uno" in game:
                continue
            bot.load_extension("GamePack.{}".format(game[:-3]))
    bot.run(os.getenv("BOT_SECRET_GAMER"))
    conn.cursor.close()
    print("{:^50}".format("~ Session Ended, OOF! ~"))