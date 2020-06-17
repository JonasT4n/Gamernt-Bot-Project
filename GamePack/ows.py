import discord
import random
import asyncio
import datetime
from discord.ext import commands
from Settings.MyUtility import checkin_guild, get_prefix
from Settings.MongoManager import MongoManager

WHITE = 0xfffffe

class OWS(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.mongodbm = MongoManager(collection="guilds")

    # Listener Area

    @commands.Cog.listener()
    async def on_ready(self):
        print("One Word Story Game is Ready!")

    # Checker Area

    def check_on_play(self, channel: discord.TextChannel):
        def inner_check(message: discord.Message):
            if not isinstance(message.channel, discord.DMChannel) and channel == message.channel and len(message.content.split(" ")) == 1:
                return True
            else:
                return False
        return inner_check

    @staticmethod
    def is_number(string: str):
        for word in string:
            if not (48 <= ord(word) < 58):
                return False
        return True

    @staticmethod
    def space_check(current_sentence: str, add: str) -> str:
        if not current_sentence.endswith(" "):
            current_sentence += " "
        return current_sentence + add

    # Command Area

    @commands.command(name="ows", aliases=["OWS", "OWs", "Ows", "OwS", "oWS", "oWs", "owS"])
    async def _one_word_story(self, ctx: commands.Context, *args):
        list_of_stories: list = checkin_guild(ctx.guild.id)["stories"]
        if len(args) == 0:
            await self.print_help(ctx.channel)
        else: 
            # Play
            if args[0].lower() == "-p" or args[0].lower() == "play":
                await self.ows_on_play(ctx.channel)

            # Help
            elif args[0].lower() == "-h" or args[0].lower() == "help":
                await self.print_help(ctx.channel)

            # Read Story
            elif args[0].lower() == "-r":
                story_num: int = random.randint(1, len(list_of_stories))
                if len(args) == 2:
                    isnum: bool = self.is_number(args[1])
                    story_num = int(args[1]) if isnum is True else random.randint(1, len(list_of_stories))
                picked_story: dict = list_of_stories[story_num - 1]
                emb = discord.Embed(
                    title= picked_story['title'],
                    description= picked_story['story'],
                    colour= discord.Colour(WHITE)
                    )
                emb.set_footer(text= f"Made on: {picked_story['date-made']}")
                await ctx.send(embed= emb)

            # Guild own Story
            elif args[0].lower() == "-os":
                if len(args) == 2:
                    isnum: bool = self.is_number(args[1])
                    args[1] = int(args[1]) if isnum is True else 1
                    await self.load_story(ctx.channel, ctx.author, page= args[1])
                else:
                    await self.load_story(ctx.channel, ctx.author)

            # Delete Story
            elif args[0].lower() == "-del":
                if len(args) < 2:
                    emb_err = discord.Embed(
                        title= "📚 One Word Story | Delete Story",
                        colour= discord.Colour(WHITE)
                        )
                    emb_err.add_field(
                        name= "How to Use?",
                        value= "Use this Command seperated with space and followed by -del and index of story you like to delete."
                            f"Example Command to delete index number 1: {get_prefix(ctx.guild.id)}ows -del 1",
                        inline= False
                        )
                    await ctx.send(embed= emb_err)
                else:
                    isnum: bool = self.is_number(args[1])
                    if isnum is False:
                        emb_err = discord.Embed(
                            title= "📚 One Word Story | Delete Story",
                            colour= discord.Colour(WHITE)
                            )
                        emb_err.add_field(
                            name= "How to Use?",
                            value= "Use this Command seperated with space and followed by -del and index of story you like to delete."
                                f"Example Command to delete index number 1: {get_prefix(ctx.guild.id)}ows -del 1",
                            inline= False
                            )
                        await ctx.send(embed= emb_err)
                    else:
                        index: int = int(args[1]) - 1
                        await ctx.send(content= f"Successfully deleted story with title : {list_of_stories[index]['title']}")
                        self.mongodbm.UnsetItem({"guild_id": str(ctx.guild.id)}, {f"stories.{index}": list_of_stories[index]})
                        self.mongodbm.UpdateObject({"guild_id": str(ctx.guild.id)}, {"$pull": {"stories": None}})
            
            # How to Play
            elif args[0].lower() == "-how":
                await self.manual(ctx.channel)
    
    # Play Area

    async def ows_on_play(self, channel: discord.TextChannel):
        # Inner Function
        def check_user_sent_title(p: discord.User):
            def inner_check(message: discord.Message):
                if p == message.author and channel == message.channel:
                    return True
                else:
                    return False
            return inner_check

        # Initialize Game
        story: str = ""
        counter: int = 0
        emb: discord.Embed = discord.Embed(
            title = "📚 One Word Story | On Going",
            description = "```All Words in Here```",
            colour = discord.Colour(WHITE)
        )
        emb.set_footer(text = f"Latest Word Sent : [Time] [Player Name]")
        hm: discord.Message = await channel.send(embed = emb)

        # Gameplay
        try:
            while True:
                get_msg: discord.Message = await self.bot.wait_for(
                    event= "message",
                    check= self.check_on_play(channel),
                    timeout= 86400.0
                    )
                if get_msg.content == "UNDO":
                    list_words: list = story.split(" ")
                    story = " ".join(list_words[:len(list_words) - 1])
                    emb: discord.Embed = discord.Embed(
                        title = "📚 One Word Story | On Going",
                        description = story,
                        colour = discord.Colour(WHITE)
                    )
                    emb.set_footer(text = f"Latest Word Sent : by {get_msg.author.name} at {datetime.datetime.now().strftime('%H:%M, %B %d %Y')}")
                    await hm.edit(embed = emb)

                elif get_msg.content == "THEEND":
                    await hm.delete()
                    last_msg: discord.Message = await channel.send(
                        content= f"{get_msg.author.mention}, Please Give the Best Title!", 
                        embed= emb
                        )
                    story_title = await self.bot.wait_for(
                        event= "message",
                        check= check_user_sent_title(get_msg.author)
                        )
                    book: dict = {
                        "title": story_title.content,
                        "story": story,
                        "date-made": datetime.datetime.now().strftime('%B %d %Y')
                        }
                    emb: discord.Embed = discord.Embed(
                        title= f"{book['title']}",
                        description= story,
                        colour= discord.Colour(WHITE)
                        )
                    await last_msg.delete()
                    emb.set_footer(text = f"Made on: {book['date-made']}")
                    await channel.send(embed = emb)
                    self.mongodbm.UpdateObject({"guild_id": str(channel.guild.id)}, {"$push": {"stories": book}})
                    break
                
                elif get_msg.content == "CANCEL":
                    emb: discord.Embed = discord.Embed(
                        title= "Game Forfeited, You have lost your Current Story.",
                        description= f"__**Story on Board :**__ \n{story}",
                        colour= discord.Colour(WHITE)
                        )
                    await hm.edit(embed = emb)
                    break

                elif get_msg.content.startswith(get_prefix(channel.guild.id)):
                    continue

                else:
                    story = self.space_check(story, get_msg.content)
                    emb: discord.Embed = discord.Embed(
                        title= "📚 One Word Story | Set Title",
                        description= story,
                        colour= discord.Colour(WHITE)
                        )
                    emb.set_footer(text= f"Latest Word Sent : by {get_msg.author.name} at {datetime.datetime.now().strftime('%H:%M, %B %d %Y')}")
                    if counter > 10:
                        counter -= 11
                        await hm.delete()
                        hm = await channel.send(embed = emb)
                    else:
                        await hm.edit(embed = emb)

                counter += 1

        except asyncio.TimeoutError:
            emb = discord.Embed(
                title = "24 hours have passed since last Sent Message.\nGame forfeited and story has been deleted :(",
                colour = discord.Colour(WHITE)
                )
            await hm.edit(embed = emb)
        
    # Others

    async def load_story(self, channel: discord.TextChannel, person: discord.User, *, page: int = 1):
        stories: list = checkin_guild(channel.guild.id)["stories"]
        sum_stacks: int = len(stories) // 10 if len(stories) % 10 == 0 else len(stories) // 10 + 1 # Cut into Several Pages
        page = sum_stacks if page > sum_stacks else page

        def emb_maker() -> discord.Embed:
            desc: str = "```"
            for s in range((page - 1) * 10, page * 10):
                if len(stories) > s:
                    desc += f"{s + 1}. {stories[s]['title']}\n" if s != page * 10 - 1 else f"{stories[s]['title']}"
                else:
                    break
            desc += "```"
            emb = discord.Embed(
                title= f"📚 One Word Story | {channel.guild.name}'s Library",
                description= desc,
                colour= discord.Colour(WHITE)
                )
            emb.set_footer(text= f"Page {page}/{sum_stacks} | {get_prefix(channel.guild.id)}ows -r <num> to Read the Story")
            return emb

        if len(stories) <= 0:
            e = discord.Embed(
                title= f"📚 One Word Story | {channel.guild.name}'s Library",
                description= "Library is empty. Make your own story now!",
                colour= discord.Colour(WHITE)
                )
            e.set_footer(text= f"{get_prefix(channel.guild.id)}ows -p to start making story.")
            await channel.send(embed= e)
        else:
            try:
                hm: discord.Message = await channel.send(embed = emb_maker())
                await hm.add_reaction("⬅️")
                await hm.add_reaction("➡️")
                while True:
                    r: discord.Reaction
                    u: discord.User
                    r, u = await self.bot.wait_for(
                        event = "reaction_add",
                        check = lambda reaction, user : True if user == person and (str(reaction.emoji) == "➡️" or str(reaction.emoji) == "⬅️") else False,
                        timeout = 30.0
                    )
                    if str(r.emoji) == "➡️":
                        page += 1 if page < sum_stacks else 0
                    else:
                        page -= 1 if page > 0 else 0
                    await r.remove(u)
                    await hm.edit(embed = emb_maker())
            except asyncio.TimeoutError:
                pass

    @staticmethod
    async def manual(channel: discord.TextChannel):
        emb: discord.Embed = discord.Embed(
            title= "📚 One Word Story | Manual",
            colour= discord.Colour(WHITE)
            )
        emb.add_field(
            name= "Goal :",
            value= "> Make a Story by Sending a word each person. Everyone in the Channel can Participate.",
            inline= False
            )
        emb.add_field(
            name= "Rules :",
            value= "> 1. Anyone can send a message but only 1 Word\n"
                "> 2. If you send a message more than 1 word will be ignored\n"
                "> 3. If 24 hours have passed since last word sent, Game will be forfeited\n"
                "> 4. You can send as much message as you wanted to make story",
            inline= False
            )
        emb.add_field(
            name= "Utility (Use this while in Gameplay):",
            value= "> Send this message to edit the current on going story\n"
                "> `UNDO` - Undo last written word if you had any mistake\n"
                "> `THEEND` - Finish the story game. anyone who send this must set a title.\n"
                "> `CANCEL` - Cancel the game. Warning, current on going story will be lost",
            inline= False
            )
        await channel.send(embed= emb)
    
    @staticmethod
    async def print_help(channel: discord.TextChannel):
        pref: str = get_prefix(channel.guild.id)
        emb = discord.Embed(
            title="📚 One Word Story | Help",
            colour=discord.Colour(WHITE)
            )
        emb.add_field(
            name= "Command :",
            value= f"> `{pref}ows <option>`",
            inline= False
            )
        emb.add_field(
            name= "Options :",
            value= "> `-p` `play` - Start game in the channel\n"
                "> `-h` `help` - Help about one word story\n"
                "> `-r <num>` - Read your story\n"
                "> `-os <page>` - Books sriten by server\n"
                "> `-del <index>` - Delete server story\n"
                "> `-how` - How to play ows game",
            inline= False
            )
        emb.set_footer(text= f"Example Command: {pref}ows -p")
        await channel.send(embed=emb)

def setup(bot):
    bot.add_cog(OWS(bot))