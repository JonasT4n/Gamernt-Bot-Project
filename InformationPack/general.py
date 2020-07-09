import discord
import datetime
from discord.ext import commands
from Settings.MyUtility import checkin_guild, checkin_member, get_prefix, set_prefix, db_mbr, db_rpt

WHITE = 0xfffffe
current_version: str = "Version 2.1.1a"

class General(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Commands Area
    
    @commands.command()
    async def ping(self, ctx: commands.Context):
        """Ping Command, Check Bot Latency."""
        await ctx.send("🏓 `Pong! {}ms`".format(int(self.bot.latency * 1000)))

    @commands.command(name="about", aliases=['info', 'a'])
    async def _info(self, ctx: commands.Context):
        """Information About Gamern't RPG."""
        emb = discord.Embed(
            title="🎮 Gamern't Bot 🎮", 
            description= "Gamern't RPG is a RPG Game with massive Battlefield to play Multiplayer. Make your own Move, Your own Items and even Your own Equipment. Chemistry your way in Battle Mode and be the Best Play Maker.", 
            colour=WHITE
            )
        emb.set_thumbnail(url=self.bot.user.avatar_url)
        emb.set_footer(text=f"{current_version}")
        await ctx.send(embed=emb)

    @commands.command(name="new", aliases=['news'])
    async def _news(self, ctx: commands.Context):
        """News about Current Bot Progress."""
        emb = discord.Embed(
            title="📰 Breaking News!", 
            description=open("./news.txt", 'r').read(), 
            colour=WHITE
            )
        emb.set_thumbnail(url=self.bot.user.avatar_url)
        emb.set_footer(text=f"{current_version}")
        await ctx.send(embed=emb)

    @commands.command(aliases=['pfix'])
    async def prefix(self, ctx: commands.Context, new_prefix: str):
        """A Command that can change the server prefix for Bot usage."""
        if len(new_prefix.split(' ')) > 1 or len(new_prefix) > 10 or " " in new_prefix:
            emb = discord.Embed(
                title="🔧 Bad Prefix!",
                description="Your Prefix might too long or bad format, try Simpler!\nFor Example : `g.` `game!` `g!`",
                colour=WHITE
                )
            await ctx.send(embed=emb)
        else:
            set_prefix(ctx.guild, new_prefix)
            emb = discord.Embed(
                title="🔧 New Prefix!",
                description=f"Server new Prefix **{new_prefix}**",
                colour=WHITE
                )
            emb.set_footer(text=f"Type {new_prefix}ping to Test it Out!")
            await ctx.send(embed=emb)

    @commands.command(name="feedback", aliases=['fb', 'report'])
    async def _feedback(self, ctx: commands.Context, *, args: str):
        """Feedback, Report and Bug Glitch Information direct from User."""
        db_rpt.UpdateObject({"_n": 0}, 
            {"$push": { "report": {
                "user": ctx.author.name,
                "id": str(ctx.author.id),
                "said": args,
                "at": str(datetime.datetime.now().strftime("%B %d %Y; %H:%M:%S"))
                }
            }})
        emb = discord.Embed(
            title="Your Feedback, Report or Suggestion has been Sent. Thank You :)",
            description=f"```{args}```",
            colour=WHITE
            )
        await ctx.send(embed=emb)

    @commands.command(name="purgemsg")
    @commands.is_owner()
    async def _purge(self, ctx: commands.Context, limit: int):
        await ctx.channel.purge(limit = limit + 1)

    @commands.command(name="shutdown")
    @commands.is_owner()
    async def _shutdown(self, ctx: commands.Context):
        await ctx.message.add_reaction("❗")
        await ctx.bot.logout()

    @commands.command(name="globalinfo", aliases=["ginfo"])
    @commands.is_owner()
    async def _global_info(self, ctx: commands.Context):
        members: int = 0
        for guild in self.bot.guilds:
            members += len(guild.members)
        emb = discord.Embed(title="📈 Stats 📈", colour=WHITE)
        emb.add_field(name="Server Count", value=f"{len(self.bot.guilds)}")
        emb.add_field(name="Member Count", value=f"{members}")
        emb.add_field(name="Shard Count", value=f"{self.bot.shard_count}")
        await ctx.send(embed=emb)

    @commands.command(name="clearbotdataindb")
    @commands.is_owner()
    async def _clearbotdataindb(self, ctx: commands.Context):
        count: int = 0
        for i in db_mbr.FindObject({}):
            member_id: int = int(i['member_id'])
            a: discord.User = self.bot.get_user(member_id)
            if a:
                if a.bot is True:
                    db_mbr.DeleteOneObject({'member_id': str(member_id)})
                    count += 1
        await ctx.send(f"Removed {count} Data(s).")

def setup(bot: commands.Bot):
    bot.add_cog(General(bot))