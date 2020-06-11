import discord
import datetime
from discord.ext import commands
from Settings.MyUtility import checkin_guild, checkin_member, get_prefix, set_prefix
from Settings.MongoManager import MongoManager

WHITE = 0xfffffe
current_version: str = "Version 2.0.1a"

class General(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.report = MongoManager(collection= "report")

    # Commands Area
    
    @commands.command()
    async def ping(self, ctx: commands.Context):
        """
        
        Ping Command, Check Bot Latency.
        
        """
        await ctx.send("🏓 `Pong! {}ms`".format(int(self.bot.latency * 1000)))

    @commands.command(name= "about", aliases= ['a'])
    async def _info(self, ctx: commands.Context):
        """
        
        Information About Gamern't RPG
        
        """
        emb = discord.Embed(
            title="🎮 Gamern't Bot 🎮", 
            description= "Gamern't RPG is a RPG Game with massive Battlefield to play Multiplayer. Make your own Move, Your own Items and even Your own Equipment. Chemistry your way in Battle Mode and be the Best Play Maker.", 
            colour=discord.Colour(WHITE)
            )
        emb.set_thumbnail(url = self.bot.user.avatar_url)
        emb.set_footer(text = f"{current_version}")
        await ctx.send(embed = emb)

    @commands.command(name= "new", aliases= ['news'])
    async def _news(self, ctx: commands.Context):
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

    @commands.command(name= "help", aliases= ['h'])
    async def _help(self, ctx: commands.Context):
        """
        
        Custom Help Command.
        
        """
        pref: str = get_prefix(ctx.guild.id)
        emb = discord.Embed(
            title= "📝 Help | Menu",
            description= "Type prefix followed by one of these command.\n"
                f"Example Command : **{pref}ping**",
            colour= discord.Colour(WHITE)
            )
        emb.add_field(
            name= "General Commands :",
            value= "> `ping` - PING. PONG!\n"
                "> `about` `a` - Bot information\n"
                "> `news` - What's new?\n"
                "> `help` `h` - This help command\n"
                "> `prefix` `pfix` - Change prefix\n"
                "> `feedback` `fb` - Send message to creator\n"
                "> `settitle` `st` - Change profile title\n"
                "> `prof` `user` - User profile\n"
                "> `img` `pict` - Search picture",
            inline= False
            )
        emb.add_field(
            name= "Fun and Game Commands :",
            value= "> `chance` - Your chance of\n"
                "> `choose` - Random chooser machine\n"
                "> `duel` - Duel simulation\n"
                "> `dice` - Roll the dice\n"
                "> `dig` `mine` - Mining is fun\n"
                "> `ows` - One Word Story game\n"
                "> `pool` - 8Pool says\n"
                "> `ask` - Ask me anything\n"
                "> `rps` - Rock Paper Scissor\n"
                "> `scramble` `scr` - Guess Scramble Word\n"
                "> `slot` - Slot Machine",
            inline= False
            )
        emb.add_field(
            name= "RPG Commands :",
            value= "> `start` - Getting started with RPG\n"
                "> `adventure` `adv` - Virtual adventure\n"
                "> `battle` - Battle multiplayer\n"
                "> `buy` - Buy something in shop\n"
                "> `item` - Managing item\n"
                "> `inv` - Your inventory\n"
                "> `equip` - Managing equipment\n"
                "> `learn` - Learn any moves in server\n"
                "> `moves` `learned` - See your current skill\n"
                "> `make` - Make item, equipment or move\n"
                "> `skillres` - Reset your skill point\n"
                "> `cur` - Manage server currency\n"
                "> `shop` - Server shop and menu\n"
                "> `stat` - Your detail in RPG",
            inline= False
            )
        emb.set_thumbnail(url= self.bot.user.avatar_url)
        emb.set_footer(text= current_version)
        await ctx.message.add_reaction("👍")
        await ctx.author.send(embed= emb)

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

    @commands.command(name= "purgemsg", pass_context= True)
    @commands.is_owner()
    async def _purge(self, ctx: commands.Context, limit: int):
        await ctx.channel.purge(limit = limit + 1)

    @commands.command(name= "shutdown", pass_context= True)
    @commands.is_owner()
    async def _shutdown(self, ctx: commands.Context):
        await ctx.message.add_reaction("❗")
        await ctx.bot.logout()

    @commands.command(name= "globalinfo", aliases= ["ginfo"], pass_context= True)
    @commands.is_owner()
    async def _global_info(self, ctx: commands.Context):
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