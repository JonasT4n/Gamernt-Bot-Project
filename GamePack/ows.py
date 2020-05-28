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
    def space_check(current_sentence: str, add: str) -> str:
        if not current_sentence.endswith(" "):
            current_sentence += " "
        return current_sentence + add

    # Command Area

    @commands.command(aliases=["OWS", "OWs", "Ows", "OwS", "oWS", "oWs", "owS"])
    async def ows(self, ctx: commands.Context, *args):
        if len(args) == 0:
            await self.print_help(ctx.channel)
        else: 
            # Play
            if args[0].lower() == "-p":
                await self.ows_on_play(ctx.channel)

            # Help
            elif args[0].lower() == "-h":
                await self.print_help(ctx.channel)

            # Read Story
            elif args[0].lower() == "-r":
                pass

            # Guild own Story
            elif args[0].lower() == "-os":
                pass

            # Delete Story
            elif args[0].lower() == "-del":
                pass
            
            # How to Play
            elif args[0].lower() == "-how":
                await self.manual(ctx.channel)
            
            # Else
            else:
                await self.print_help(ctx.channel)
    
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
            title = "📚 One Word Story",
            description = "```All Words in Here```",
            colour = discord.Colour(WHITE)
        )
        emb.set_footer(text = f"Latest Word Sent : [Time] [Player Name]")
        hm: discord.Message = await channel.send(embed = emb)

        # Gameplay
        try:
            while True:
                get_msg: discord.Message = await self.bot.wait_for(
                    event = "message",
                    check = self.check_on_play(channel),
                    timeout = 86400.0
                )
                if get_msg.content == "UNDO":
                    list_words: list = story.split(" ")
                    story = " ".join(list_words[:len(list_words) - 1])
                    emb: discord.Embed = discord.Embed(
                        title = "📚 One Word Story",
                        description = story,
                        colour = discord.Colour(WHITE)
                    )
                    emb.set_footer(text = f"Latest Word Sent : by {get_msg.author.name} at {datetime.datetime.now().strftime('%H:%M, %B %d %Y')}")
                    await hm.edit(embed = emb)

                elif get_msg.content == "THEEND":
                    await hm.delete()
                    last_msg: discord.Message = await channel.send(
                        content=f"{get_msg.author.mention}, Please Give the Best Title!", 
                        embed = emb
                    )
                    story_title = await self.bot.wait_for(
                        event = "message",
                        check = check_user_sent_title(get_msg.author)
                    )
                    book: dict = {
                        "title": story_title.content,
                        "story": story,
                        "date-made": datetime.datetime.now().strftime('%B %d %Y')
                    }
                    emb: discord.Embed = discord.Embed(
                        title = f"{book['title']}",
                        description = story,
                        colour = discord.Colour(WHITE)
                    )
                    await last_msg.delete()
                    emb.set_footer(text = f"Made on : {book['date-made']}")
                    await channel.send(embed = emb)
                    self.mongodbm.UpdateObject({"guild_id": str(channel.guild.id)}, {"$push": {"stories": book}})
                    break
                
                elif get_msg.content == "CANCEL":
                    emb: discord.Embed = discord.Embed(
                        title = "Game Forfeited, You have lost your Current Story.",
                        description = f"__**Story on Board :**__ \n{story}",
                        colour = discord.Colour(WHITE)
                    )
                    await hm.edit(embed = emb)
                    break

                elif get_msg.content.startswith(get_prefix(self.mongodbm, channel.guild.id)):
                    continue

                else:
                    story = self.space_check(story, get_msg.content)
                    emb: discord.Embed = discord.Embed(
                        title = "📚 One Word Story",
                        description = story,
                        colour = discord.Colour(WHITE)
                    )
                    emb.set_footer(text = f"Latest Word Sent : by {get_msg.author.name} at {datetime.datetime.now().strftime('%H:%M, %B %d %Y')}")
                    if counter > 10:
                        counter -= 11
                        await hm.delete()
                        hm = await channel.send(embed = emb)
                    else:
                        await hm.edit(embed = emb)

                counter += 1

        except asyncio.TimeoutError:
            emb = discord.Embed(
                title = "8 hours have passed since last Sent Message.\nGame forfeited and story has been deleted :(",
                colour = discord.Colour(WHITE)
            )
            await hm.edit(embed = emb)
        
    # Others

    def load_story(self, guild_id: int):
        pass

    @staticmethod
    async def manual(channel: discord.TextChannel):
        emb = discord.Embed(
            title="📚 One Word Story | Manual",
            description=open("./Help/ows_manual.txt").read(),
            colour=discord.Colour(WHITE)
        )
        await channel.send(embed=emb)
    
    @staticmethod
    async def print_help(channel: discord.TextChannel):
        emb = discord.Embed(
            title="📚 One Word Story | Help",
            description=open("./Help/owsh.txt").read(),
            colour=discord.Colour(WHITE)
        )
        emb.set_footer(text="Example Command: g.ows -p")
        await channel.send(embed=emb)

def setup(bot):
    bot.add_cog(OWS(bot))