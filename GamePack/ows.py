import discord
from discord.ext import commands
from Settings.Handler import *
import asyncio, random, threading
from Settings.DbManager import DbManager as dbm

WHITE = 0xfffffe

class OWS(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.db = dbm.connect_db("./DataPack/ows_game.db")

    def check_in_game_command(self, channel_id):
        def inner_check(message):
            if channel_id == message.channel.id:
                return True
            else:
                return False
        return inner_check

    def check_last_person_ows_give_title(self, author):
        def inner_check(message):
            if author.id == message.author.id:
                return True
            else:
                False
        return inner_check

    def check_choosen_story(self, author, list_story: list):
        def inner_check(message):
            try:
                if message.author == author and (int(message.content) > 0 and int(message.content) <= len(list_story)):
                    return True
                else:
                    return False
            except Exception as exc:
                print(type(exc), exc)
                return False
        return inner_check

    async def ows_gameplay(self, ctx):
        # Initialize first
        emb = discord.Embed(colour=discord.Colour(WHITE))
        chn_id = ctx.message.channel.id

        # Attribute in-game
        next_value = []
        on_play = True
        new_emb = discord.Embed(colour=discord.Colour(WHITE))
        handler_sent_emb = discord.Embed(description="***Current Progress***", colour=discord.Colour(WHITE))
        emb.add_field(name="📖 OWS (Game Started)", value="Send a single Word by different person to make a Story.")
        emb.set_footer(text="type 'THE END' to end the Game. type 'UNDO' to undo a word. type 'CANCEL' to cancel the Game.")
        this_message = await ctx.send(embed=emb)
        other_message = await ctx.send(embed=handler_sent_emb)
        lastPerson = ctx.message.author

        # Game started only in The Channel
        try:
            chains = 0
            while on_play:
                new_word = await self.bot.wait_for(event="message", check=self.check_in_game_command(chn_id), timeout=2000.0)
                if new_word.content == "THE END" and new_word.channel.id == chn_id:
                    lastPerson = new_word.author
                    on_play = False
                elif new_word.content == "UNDO" and new_word.channel.id == chn_id:
                    if len(next_value) == 0:
                        continue
                    del next_value[len(next_value) - 1]
                    handler_sent_emb = discord.Embed(description=" ".join(next_value), colour=discord.Colour(WHITE))
                    await other_message.edit(embed=handler_sent_emb)
                elif new_word.content == "CANCEL" and new_word.channel.id == chn_id:
                    await ctx.send(content="*Game has been Cancelled, Ok Next Time!*")
                    await other_message.delete()
                    await this_message.delete()
                elif new_word.channel.id == chn_id and len(new_word.content.split(' ')) == 1:
                    next_value.append(new_word.content)
                    chains += 1
                    if chains >= 25:
                        chains -= 25
                        handler_sent_emb = discord.Embed(description=" ".join(next_value), colour=discord.Colour(WHITE))
                        await other_message.delete()
                        other_message = await ctx.send(embed=handler_sent_emb)
                    else:
                        handler_sent_emb = discord.Embed(description=" ".join(next_value), colour=discord.Colour(WHITE))
                        await other_message.edit(embed=handler_sent_emb)
                else:
                    continue

        except asyncio.TimeoutError:
            new_emb.add_field(name="Game Time Out!", value=" ".join(next_value), inline=True)
            new_emb.set_footer(text="Consequence : This Story will not be Saved.")
            await ctx.send(embed=new_emb)
            await other_message.delete()
            await this_message.delete()
        else:
            # Last Response Before The Game End, Save it into Database
            this_handler_message_author_last = await ctx.send("{} please give a Title for this Story.".format(lastPerson.mention))
            title_story = await self.bot.wait_for(event="message", check=self.check_last_person_ows_give_title(lastPerson))
            await this_handler_message_author_last.delete()
            self.db.cursor.execute("""INSERT INTO ows_results VALUES(:svr_id, :chn_id, :title, :story)""", {"svr_id":str(title_story.guild.id), "chn_id":str(chn_id), "title":title_story.content, "story":" ".join(next_value)})
            self.db.connect.commit()
            new_emb.add_field(name="📖 {}".format(title_story.content), value=" ".join(next_value), inline=False)
            await ctx.send(embed=new_emb)
            await other_message.delete()
            await this_message.delete()

    async def random_call_story(self, ctx):
        temp_conn = dbm.connect_db("./DataPack/ows_game.db")
        temp_conn.cursor.execute("""SELECT story_title, story FROM ows_results""")
        get_story = random.choice(temp_conn.cursor.fetchall())
        temp_conn.cursor.close()
        emb = discord.Embed(title="📖 Random Story", colour=discord.Colour(WHITE))
        emb.add_field(name="{}".format(get_story[0]), value="{}".format(get_story[1]))
        await ctx.send(embed=emb)

    async def show_list_story(self, ctx):
        emb = discord.Embed(colour=discord.Colour(WHITE))
        self.db.cursor.execute("""SELECT * FROM ows_results WHERE server_id=:sid""", {"sid":str(ctx.message.guild.id)})
        list_of_server_stories = self.db.cursor.fetchall()
        titles = ""
        if list_of_server_stories is None or len(list_of_server_stories) == 0:
            emb.add_field(name="Your Server Stories", value="```There is No Stories Yet.```")
        else:
            long_page = (len(list_of_server_stories) // 20) + 1
            for i in range(len(list_of_server_stories)):
                if i == 0:
                    titles += "{}. ".format(i + 1) + list_of_server_stories[i][2]
                else:
                    titles += "\n{}. {}".format(i + 1, list_of_server_stories[i][2])
            emb.add_field(name="Your Server Stories", value="```{}```".format(titles), inline=False)
        return list_of_server_stories, await ctx.send(embed=emb)

    async def help_ows(self, ctx):
        emb = discord.Embed(colour=discord.Colour(WHITE))
        emb.set_author(name="📖 One Word Story")
        emb.add_field(name="Commands (alias):", value=open("./DataPack/Help/owsh.txt", 'r').read(), inline=False)
        emb.set_footer(text="Example Command : g.ows how")
        await ctx.send(embed=emb)

    @commands.command(aliases=["OWS", "OWs", "Ows", "OwS", "oWS", "oWs", "owS"],)
    async def ows(self, ctx, stat: str, story_num = None):
        statuses = ["start", "h", "help", "rdm", "random", "ourstory", "os", "how", "delete", "del", "read", "r"]
        if stat.lower() not in statuses: # None of these known on this Command
            await self.help_ows(ctx)

        if stat.lower() == "help" or stat.lower() == "h": # Need Help about OWS
            await self.help_ows(ctx)

        if stat.lower() == "start": # Start New Game
            threading.Thread(target=await self.ows_gameplay(ctx)).start()
            
        if stat.lower() == "how": # How to Play One Word Story
            emb = discord.Embed(title="~ One Word Story ~", description="**1.** Choose the Channel where you want to play it.\n**2.** Type the Command '**Start**'\n**3.** Each player send one word to make a story as long as you wanted.\n**4.** Type '**THE END**' to finish the Story.\n**5.** Whoever ends it must Give a Title of the Story.", colour=discord.Colour(WHITE))
            emb.set_footer(text="")
            await ctx.send(embed=emb)
            
        if stat.lower() == "ourstory" or stat.lower() == "os": # Own Server Story to Look Up
            await self.show_list_story(ctx)
        
        if stat.lower() == "read" or stat.lower() == "r": # Choose and Read server own story
            list_svr_story, temp_msg = await self.show_list_story(ctx)
            try:
                xmsg = await ctx.send("***Pick a Story you want to read By Number.***")
                temp_msg1 = await self.bot.wait_for(event="message", check=self.check_choosen_story(ctx.message.author, list_svr_story), timeout=60.0)
                picked_story = list_svr_story[int(temp_msg1.content) - 1]
                emb_story = discord.Embed(title=picked_story[2], description=picked_story[3], colour=discord.Colour(WHITE))
                await ctx.send(embed=emb_story)
                await temp_msg1.delete()
                await temp_msg.delete()
                await xmsg.delete()
            except asyncio.TimeoutError:
                await temp_msg.delete()
                await xmsg.delete()
                await ctx.send("*Request Timeout.*")

        if stat.lower() == "random" or stat.lower() == "rdm": # Random Generate Story
            await self.random_call_story(ctx)
            
        if (stat.lower() == "delete" or stat.lower() == "del") and (ctx.message.author.guild_permissions.ban_members or ctx.message.author.guild_permissions.administrator or ctx.message.author.guild_permissions.kick_members) :
            list_svr_story, temp_msg = await self.show_list_story(ctx)
            try:
                xmsg = await ctx.send("***Pick a Story you want to read By Number.***")
                temp_msg1 = await self.bot.wait_for(event="message", check=self.check_choosen_story(ctx.message.author, list_svr_story), timeout=60.0)
                picked_story = list_svr_story[int(temp_msg1.content) - 1]
                self.db.cursor.execute("""DELETE FROM ows_results WHERE server_id=:sid AND story=:story""", {"sid":str(ctx.message.guild.id), "story":picked_story[3]})
                await ctx.send("You have thrown away your **{}** Book.".format(picked_story[2]))
                await temp_msg.delete()
                await temp_msg1.delete()
            except asyncio.TimeoutError:
                await temp_msg.delete()
                await xmsg.delete()
            except commands.MissingPermissions:
                emb = discord.Embed(colour=discord.Colour(WHITE))
                emb.add_field(name="You Can't Delete Story", value="`You Don't Have Permission to do that.`")
                await ctx.send(embed = emb)

    @ows.error # Occure OWS error
    async def ows_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            emb = discord.Embed(colour=discord.Colour(WHITE))
            emb.set_author(name="~ One Word Story ~")
            emb.add_field(name="Commands (alias):", value=open("./DataPack/Help/owsh.txt", 'r').read(), inline=False)
            await ctx.send(embed=emb)

def setup(bot):
    bot.add_cog(OWS(bot))