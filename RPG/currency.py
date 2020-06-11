import discord
import re
from discord.ext import commands
from Settings.MyUtility import checkin_guild, get_prefix
from Settings.MongoManager import MongoManager

WHITE = 0xfffffe

class Currency(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.gdb = MongoManager(collection= "guilds")

    # Event Listener Area

    @commands.Cog.listener()
    async def on_ready(self):
        print("Currency Manager is Ready!")

    # Checker Area

    @staticmethod
    def check_emoji(emo: str):
        custom = re.search(r'<:\w*:\d*>', emo)
        if custom:
            return custom[0]
        else:
            unicode: str = emo.encode("unicode-escape").decode("ASCII")
            if "\\U" in unicode:
                return "\\U" + unicode.split('\\U')[1]
            else:
                return None

    @staticmethod
    def is_number(string: str):
        for word in string:
            if not (48 <= ord(word) < 58):
                return False
        return True

    # Commands Area

    @commands.command(name= "currency", aliases= ["cur"], pass_context= True)
    async def _currency(self, ctx: commands.Context, *args):
        if len(args) == 0:
            await self.print_help(ctx.channel)
        else:
            guild_info: dict = checkin_guild(ctx.guild.id)
            cur_type: str = guild_info['currency']['type']
            if len(args) == 2 and args[0].lower() == "-t":
                emoji = self.check_emoji(args[1])
                if emoji:
                    emb: discord.Embed
                    if "\\U" in emoji:
                        self.gdb.SetObject({"guild_id": str(ctx.guild.id)}, {
                            "currency.type": emoji.decode("unicode-escape")
                            })
                        emb = discord.Embed(
                            title= "Server New Currency!",
                            description= f"> Server {ctx.guild.name} Currency is now " + emoji.decode("unicode-escape"),
                            colour= discord.Colour(WHITE)
                            )
                    else:
                        self.gdb.SetObject({"guild_id": str(ctx.guild.id)}, {
                            "currency.type": emoji
                            })
                        emb = discord.Embed(
                            title= "Server New Currency!",
                            description= f"> Server {ctx.guild.name} Currency is now " + emoji,
                            colour= discord.Colour(WHITE)
                            )
                    await ctx.send(embed= emb)

            elif args[0].lower() == "-get":
                emb = discord.Embed(
                    title= f"🏦 {ctx.guild.name}",
                    description= f"Currency Type : {cur_type}\n"
                        f"Chat Money [min-max] : {guild_info['currency']['chat-min']}-{guild_info['currency']['chat-max']} {cur_type}",
                    colour= discord.Colour(WHITE)
                    )
                emb.set_footer(text= f"Last Modified : {guild_info['currency']['last-modified']} | By : {guild_info['currency']['modif-by']}")
                await ctx.send(embed= emb)

            elif len(args) == 2 and args[0].lower() == "-min":
                isnum: bool = self.is_number(args[1])
                if isnum is True:
                    min_in: int = int(args[1])
                    if guild_info["currency"]["chat-max"] < min_in:
                        self.gdb.SetObject({"guild_id": str(ctx.guild.id)}, {
                            "currency.chat-max": min_in
                            })
                    self.gdb.SetObject({"guild_id": str(ctx.guild.id)}, {
                        "currency.chat-min": min_in
                        })
                    updated_guild_info: dict = checkin_guild(ctx.guild.id)
                    emb = discord.Embed(
                        title= "💸 Set Chat Money Success",
                        description= f"Chat Money Increament : {updated_guild_info['currency']['chat-min']}-{updated_guild_info['currency']['chat-max']}",
                        colour= discord.Colour(WHITE)
                        )
                    await ctx.send(embed= emb)

            elif len(args) == 2 and args[0].lower() == "-max":
                isnum: bool = self.is_number(args[1])
                if isnum is True:
                    max_in: int = int(args[1])
                    if guild_info["currency"]["chat-min"] > max_in:
                        self.gdb.SetObject({"guild_id": str(ctx.guild.id)}, {
                            "currency.chat-min": max_in
                            })
                    self.gdb.SetObject({"guild_id": str(ctx.guild.id)}, {
                        "currency.chat-max": max_in
                        })
                    updated_guild_info: dict = checkin_guild(ctx.guild.id)
                    emb = discord.Embed(
                        title= "💸 Set Chat Money Success",
                        description= f"Chat Money Increament : {updated_guild_info['currency']['chat-min']}-{updated_guild_info['currency']['chat-max']}",
                        colour= discord.Colour(WHITE)
                        )
                    await ctx.send(embed= emb)

    # Others

    @staticmethod
    async def print_help(channel: discord.TextChannel):
        pref: str = get_prefix(channel.guild.id)
        emb = discord.Embed(
            title= "💸 Currency Manager | Help",
            description= "A custom server currency, set your chat money, set yout currency and "
                "use this money for several things like buy items, equipments, and learn moves.",
            colour= discord.Colour(WHITE)
            )
        emb.add_field(
            name= "Command :",
            value= f"`{pref}cur <option>`",
            inline= False
            )
        emb.add_field(
            name= "Options :",
            value= "> `-t <symbol>` - Set currency type in your server\n"
                "> `-get` Get info about server currency\n"
                "> `-min <amount>` - Set minimal getting money by chat\n"
                "> `-max <amount>` - Set maximal getting money by chat",
            inline= False
            )
        emb.set_footer(text= f"Example Command : {pref}cur -get")
        await channel.send(embed= emb)

def setup(bot: commands.Bot):
    bot.add_cog(Currency(bot))