import discord
import datetime
from discord.ext import commands
from Settings.MyUtility import checkin_guild, checkin_member, get_prefix, set_prefix
from Settings.MongoManager import MongoManager

WHITE = 0xfffffe
current_version: str = "Version 1.0.11a"

class General(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.report = MongoManager(collection = "report")

    # Commands Area
    
    @commands.command()
    async def ping(self, ctx: commands.Context):
        """
        
        Ping Command, Check Bot Latency.
        
        """
        await ctx.send("🏓 **Pong! {}ms**".format(int(self.bot.latency * 1000)))

    @commands.command(aliases=['a'])
    async def info(self, ctx: commands.Context):
        """
        
        Information About Gamern't RPG
        
        """
        emb = discord.Embed(
            title="🎮 Gamern't Bot 🎮", 
            description = open("./Help/about.txt").read(), 
            colour=discord.Colour(WHITE)
        )
        emb.set_thumbnail(url = self.bot.user.avatar_url)
        emb.set_footer(text = f"{current_version}")
        await ctx.send(embed = emb)

    @commands.command(aliases=['new'])
    async def news(self, ctx: commands.Context):
        """
        
        News about Current Bot Progress.
        
        """
        emb = discord.Embed(
            title = "📰 Breaking News!", 
            description = open("./Help/news.txt", 'r').read(), 
            colour = discord.Colour(WHITE)
        )
        emb.set_thumbnail(url = self.bot.user.avatar_url)
        emb.set_footer(text = f"{current_version}")
        await ctx.send(embed = emb)

    @commands.command(aliases=['h'])
    async def help(self, ctx: commands.Context):
        """
        
        Custom Help Command.
        
        """
        emb = discord.Embed(
            title="Help Menu",
            description= open("./Help/help_file.txt").read(),
            colour=discord.Colour(WHITE)
        )
        emb.set_thumbnail(url = self.bot.user.avatar_url)
        emb.set_footer(text = current_version)
        await ctx.send(embed = emb)

    @commands.command(aliases=['pfix'])
    async def prefix(self, ctx: commands.Context, new_prefix: str):
        """
        
        This Command for Change Server Prefix.
        
        """
        if len(new_prefix.split(' ')) > 1 or len(new_prefix) > 10 or " " in new_prefix:
            emb = discord.Embed(
                title = "🔧 Bad Prefix!",
                description = "Your Prefix might too long or bad format, try Simpler!\nFor Example : `g.` `game!` `g!`",
                colour = discord.Colour(WHITE)
            )
            await ctx.send(embed = emb)
        else:
            set_prefix(ctx.guild.id, new_prefix)
            emb = discord.Embed(
                title = "🔧 New Prefix!",
                description = f"Server new Prefix **{new_prefix}**",
                colour = discord.Colour(WHITE)
            )
            emb.set_footer(text=f"Type {new_prefix}ping to Test it Out!")
            await ctx.send(embed = emb)

    @commands.command(aliases=['fb', 'report'])
    async def feedback(self, ctx: commands.Context, *, args: str):
        """
        
        Feedback, Report and Bug Glitch Information direct from User.
        
        """
        self.report.UpdateObject(
            {"guild_id": ctx.guild.id}, 
            {"$push": { "report": {
                "user": ctx.author.name,
                "id": str(ctx.author.id),
                "said": args,
                "at": str(datetime.datetime.now().strftime("%B %d %Y; %H:%M:%S"))
            }
        }})
        emb = discord.Embed(
            title = "Your Feedback, Report or Suggestion has been Sent. Thank You :)",
            description = f"```{args}```",
            colour = discord.Colour(WHITE)
        )
        await ctx.send(embed = emb)

    @commands.command()
    @commands.is_owner()
    async def purge(self, ctx: commands.Context, limit: int):
        await ctx.channel.purge(limit = limit + 1)

    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx: commands.Context):
        await ctx.bot.logout()

    @commands.command()
    @commands.is_owner()
    async def global_info(self, ctx: commands.Context):
        members: int = 0
        for guild in self.bot.guilds:
            members += len(guild.members)
        emb = discord.Embed(
            title="📈 Stats 📈",
            colour=discord.Colour(WHITE)
        )
        emb.add_field(name="Server Count", value=f"{len(self.bot.guilds)}")
        emb.add_field(name="Member Count", value=f"{members}")
        emb.add_field(name="Shard Count", value=f"{self.bot.shard_count}")
        await ctx.send(embed = emb)

def setup(bot: commands.Bot):
    bot.add_cog(General(bot))