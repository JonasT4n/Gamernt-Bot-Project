import discord
from discord.ext import commands
from Settings.Handler import *
import asyncio, random, threading
from Settings.DbManager import DbManager as dbm

WHITE = 0xfffffe

class OWS(commands.Cog):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.conn = dbm.connect_db("./DataPack/ows_game.db")

    @commands.command(aliases=["OWS", "OWs", "Ows", "OwS", "oWS", "oWs", "owS"])
    async def ows(self, ctx, stat: str, story_num = None):
        statuses = ["start", "h", "help", "r", "random", "ourstory", "os", "how", "delete", "del"]
        try:
            if stat.lower() not in statuses:
                raise commands.BadArgument

            if stat.lower() == "help" or stat.lower() == "h": # Help
                emb = discord.Embed(colour=discord.Colour(WHITE))
                emb.set_author(name="📖 One Word Story")
                emb.add_field(name="Commands (alias):", value="""***Start*** *-> Start The Game in the Channel.*\n***Help (h)*** *-> Help about One Word Story.*\n***OurStory (os)*** *-> Books Writen by your Server.*\n***Random (r)*** *-> Generate Random Story from Everywhere.*\n***How*** *-> The Manual to play this Game.*""", inline=False)
                emb.set_footer(text="Example Command : g.ows how")
                await ctx.send(embed=emb)

            if stat.lower() == "start": # Start New Game
                threading.Thread(target=await self.ows_gameplay(ctx)).start()
                
            if stat.lower() == "how": # How to Play One Word Story
                emb = discord.Embed(title="~ One Word Story ~", description="**1.** Choose the Channel where you want to play it.\n**2.** Type the Command '**Start**'\n**3.** Each player send one word to make a story as long as you wanted.\n**4.** Type '**THE END**' to finish the Story.\n**5.** Whoever ends it must Give a Title of the Story.", colour=discord.Colour(WHITE))
                emb.set_footer(text="")
                await ctx.send(embed=emb)
                
            if stat.lower() == "ourstory" or stat.lower() == "os": # Own Server Story to Look Up
                emb = discord.Embed(colour=discord.Colour(WHITE))
                self.conn.cursor.execute("""SELECT * FROM ows_results WHERE server_id=:sid""", {"sid":str(ctx.message.guild.id)})
                list_of_server_stories, titles = self.conn.cursor.fetchall(), ""
                if list_of_server_stories is None:
                    emb.add_field(name="Your Server Stories", value="There is No Stories Yet.")
                else:
                    for i in range(len(list_of_server_stories)):
                        if i == 0:
                            titles += "{}. ".format(i + 1) + list_of_server_stories[i][2]
                        else:
                            titles += "\n{}. {}".format(i + 1, list_of_server_stories[i][2])
                    emb.add_field(name="Your Server Stories", value="```{}```".format(titles), inline=False)
                await ctx.send(embed=emb)

            if stat.lower() == "random" or stat.lower() == "r": # Random Generate Story
                await self.random_call_story(ctx)
                
            if (stat.lower() == "delete" or stat.lower() == "del") and (ctx.message.author.guild_permissions.ban_members or ctx.message.author.guild_permissions.administrator) :
                pass

        except Exception as exc:
            if type(exc) == commands.BadArgument:
                emb = discord.Embed(colour=discord.Colour(WHITE))
                emb.set_author(name="📖 One Word Story")
                emb.add_field(name="Commands (alias):", value="""***Start*** *-> Start The Game in the Channel.*\n***Help (h)*** *-> Help about One Word Story.*\n***OurStory (os)*** *-> Books Writen by your Server.*\n***Random (r)*** *-> Generate Random Story from Everywhere.*\n***How*** *-> The Manual to play this Game.*""", inline=False)
                emb.set_footer(text="Example Command : g.ows how")
                await ctx.send(embed=emb)
            elif type(exc) == commands.MissingPermissions:
                emb = discord.Embed(colour=discord.Colour(WHITE))
                emb.add_field(name="You Can't Delete Story", value="`You Don't Have Permission to do that.`")
                await ctx.send(embed = emb)
            else:
                print(type(exc), exc)

    @ows.error
    async def ows_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            emb = discord.Embed(colour=discord.Colour(WHITE))
            emb.set_author(name="~ One Word Story ~")
            emb.add_field(name="Commands (alias):", value="""***Start*** *-> Start The Game in the Channel.*\n***Help (h)*** *-> Help about One Word Story.*\n***Random (r)*** *-> Generate Random Story from Everywhere.* """, inline=False)
            await ctx.send(embed=emb)
            
    async def ows_gameplay(self, ctx):
        # Initialize first Embed
        emb = discord.Embed(colour=discord.Colour(WHITE))
        next_value, on_play, new_emb, this_channel_id = [], True, discord.Embed(colour=discord.Colour(WHITE)), ctx.message.channel.id
        handler_sent_emb = discord.Embed(description="***Current Progress per Sentence***", colour=discord.Colour(WHITE))
        emb.add_field(name="📖 OWS (Game Started)", value="Send a single Word by different person to make a Story.")
        emb.set_footer(text="type 'THE END' to end the Game. type 'UNDO' to undo a word. type 'CANCEL' to cancel the Game.")
        this_message = await ctx.send(embed=emb)
        other_message = await ctx.send(embed=handler_sent_emb)
        lastPerson = ctx.message.author
        # Game started only in The Channel
        try:
            while on_play:
                new_word = await self.bot.wait_for(event="message", check=check_user_chain(this_channel_id), timeout=86400.0)
                if new_word.content == "THE END":
                    lastPerson = new_word.author
                    on_play = False
                elif new_word.content == "UNDO":
                    if len(next_value) == 0:
                        continue
                    del next_value[len(next_value) - 1]
                    handler_sent_emb = discord.Embed(description=" ".join(next_value), colour=discord.Colour(WHITE))
                    await other_message.edit(embed=handler_sent_emb)
                elif new_word.content == "CANCEL":
                    await ctx.send(content="*Game has been Cancelled, Ok Next Time!*")
                    await other_message.delete()
                    await this_message.delete()
                else:
                    next_value.append(new_word.content)
                    handler_sent_emb = discord.Embed(description=" ".join(next_value), colour=discord.Colour(WHITE))
                    await other_message.edit(embed=handler_sent_emb)
        except asyncio.TimeoutError:
            new_emb.add_field(name="Game Time Out!", value=" ".join(next_value), inline=True)
            new_emb.set_footer(text="Consequence : This Story will not be Saved.")
            await ctx.send(embed=new_emb)
            await other_message.delete()
            await this_message.delete()
        else:
            # Last Response Before The Game End, Save it into Database
            this_handler_message_author_last = await ctx.send("{} please give a Title for this Story.".format(lastPerson.mention))
            title_story = await self.bot.wait_for(event="message", check=check_last_person_ows_give_title(lastPerson))
            await this_handler_message_author_last.delete()
            self.conn.cursor.execute("""INSERT INTO ows_results VALUES(:svr_id, :chn_id, :title, :story)""", {"svr_id":str(title_story.guild.id), "chn_id":str(this_channel_id), "title":title_story.content, "story":" ".join(next_value)})
            self.conn.connect.commit()
            new_emb.add_field(name="📖 {}".format(title_story.content), value=" ".join(next_value), inline=False)
            await ctx.send(embed=new_emb)
            await other_message.delete()
            await this_message.delete()

    async def random_call_story(self, ctx):
        temp_conn = dbm.connect_db("./DataPack/ows_game.db")
        temp_conn.cursor.execute("""SELECT story_title, story FROM ows_results""")
        get_story = random.choice(temp_conn.cursor.fetchall())
        temp_conn.cursor.close()
        emb = discord.Embed(title="~ Random Story ~", colour=discord.Colour(WHITE))
        emb.add_field(name="{}".format(get_story[0]), value="{}".format(get_story[1]))
        await ctx.send(embed=emb)

def setup(bot):
    bot.add_cog(OWS(bot))