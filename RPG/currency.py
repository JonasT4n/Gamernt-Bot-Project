import discord
import re
import datetime
import random
from discord.ext import commands
from Settings.MyUtility import checkin_guild, checkin_member, get_prefix, is_number, add_money, db_gld, db_mbr

WHITE = 0xfffffe

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

class Currency(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Event Listener Area

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Chat Money
        if not isinstance(message.channel, discord.DMChannel):
            pref: str = get_prefix(message.guild)
            guild_data: dict = checkin_guild(message.guild)
            get_money: int = random.randint(guild_data["currency"]["chat-min"], guild_data["currency"]["chat-max"])
            await add_money(message.guild.id, message.author, get_money)

    # Commands Area

    @commands.command(name="leaderboard", aliases=["lb"],)
    async def _lb(self, ctx: commands.Context):
        data = db_mbr.FindObject({}, sortby=f"backpack.money.{str(ctx.guild.id)}", limit=5)
        guid_currency: str = checkin_guild(ctx.guild)['currency']['type']
        # Create Description and Send Result
        members: list = [self.bot.get_user(int(i['member_id'])) for i in data]
        index_del: list = []
        for j in range(len(members)):
            if members[j] is None:
                index_del.append(j)
        for k in range(len(index_del), 0, -1):
            data.pop(index_del[k - 1])
            members.pop(index_del[k - 1])
        desc: list = [f"> {p+1}. {members[p].name} : {data[p]['backpack']['money'][str(ctx.guild.id)]} {guid_currency}" for p in range(len(members))]
        emb = discord.Embed(
            title="📈 Leaderboard",
            colour=WHITE
            )
        emb.add_field(
            name="🏦 Top 5 Richest in Server",
            value="\n".join(desc),
            inline=False
            )
        emb.set_thumbnail(url="https://i.dlpng.com/static/png/5698135-trophy-clipart-png-transparent-background-image-free-png-templates-trophy-clipart-png-2000_2000_preview.png")
        await ctx.send(embed=emb)

    @commands.command(name="currency", aliases=["cur"])
    async def _currency(self, ctx: commands.Context, *args):
        if len(args) == 0:
            await self.print_help(ctx.channel)
        else:
            guild_info: dict = checkin_guild(ctx.guild.id)
            cur_type: str = guild_info['currency']['type']
            person: discord.User = ctx.author

            # Change Server Currency Type
            if len(args) == 2 and args[0].lower() == "-t":
                emoji = check_emoji(args[1])
                if emoji:
                    emb: discord.Embed
                    if "\\U" in emoji:
                        partial_emoji = emoji.encode("ASCII").decode("unicode-escape")
                        db_gld.SetObject({"guild_id": str(ctx.guild.id)}, {
                            "currency.type": partial_emoji
                            })
                        emb = discord.Embed (
                            title="Server New Currency!",
                            description=f"> Server {ctx.guild.name} Currency is now {partial_emoji}",
                            colour=WHITE
                            )
                    else:
                        db_gld.SetObject({"guild_id": str(ctx.guild.id)}, {
                            "currency.type": emoji
                            })
                        emb = discord.Embed (
                            title="Server New Currency!",
                            description=f"> Server {ctx.guild.name} Currency is now " + emoji,
                            colour=WHITE
                            )
                    db_gld.SetObject({"guild_id": str(ctx.guild.id)}, {
                        "currency.modif-by": person.name,
                        "currency.last-modified": datetime.datetime.now().strftime('%B %d %Y')
                        })
                    await ctx.send(embed=emb)

            # Get Info Currency in Server
            elif args[0].lower() == "-get":
                emb = discord.Embed(
                    title=f"🏦 {ctx.guild.name}",
                    description=f"Currency Type : {cur_type}\n"
                        f"Chat Money [min-max] : {guild_info['currency']['chat-min']}-{guild_info['currency']['chat-max']} {cur_type}",
                    colour=WHITE
                    )
                emb.set_footer(text=f"Last Modified : {guild_info['currency']['last-modified']} | By : {guild_info['currency']['modif-by']}")
                await ctx.send(embed=emb)

            # Set Min Earn Money by Chatting
            elif len(args) == 2 and args[0].lower() == "-min":
                isnum: bool = is_number(args[1])
                if isnum is True:
                    min_in: int = int(args[1])
                    if guild_info["currency"]["chat-max"] < min_in:
                        db_gld.SetObject({"guild_id": str(ctx.guild.id)}, {
                            "currency.chat-max": min_in
                            })
                    db_gld.SetObject({"guild_id": str(ctx.guild.id)}, {
                        "currency.chat-min": min_in
                        })
                    updated_guild_info: dict = checkin_guild(ctx.guild.id)
                    emb = discord.Embed(
                        title="💸 Set Chat Money Success",
                        description=f"Chat Money Increament : {updated_guild_info['currency']['chat-min']}-{updated_guild_info['currency']['chat-max']}",
                        colour=WHITE
                        )
                    db_gld.SetObject({"guild_id": str(ctx.guild.id)}, {
                        "currency.modif-by": person.name,
                        "currency.last-modified": datetime.datetime.now().strftime('%B %d %Y')
                        })
                    await ctx.send(embed=emb)

            # Set Max Earn Money by Chatting
            elif len(args) == 2 and args[0].lower() == "-max":
                isnum: bool = is_number(args[1])
                if isnum is True:
                    max_in: int = int(args[1])
                    if guild_info["currency"]["chat-min"] > max_in:
                        db_gld.SetObject({"guild_id": str(ctx.guild.id)}, {
                            "currency.chat-min": max_in
                            })
                    db_gld.SetObject({"guild_id": str(ctx.guild.id)}, {
                        "currency.chat-max": max_in
                        })
                    updated_guild_info: dict = checkin_guild(ctx.guild.id)
                    emb = discord.Embed(
                        title="💸 Set Chat Money Success",
                        description=f"Chat Money Increament : {updated_guild_info['currency']['chat-min']}-{updated_guild_info['currency']['chat-max']}",
                        colour=WHITE
                        )
                    db_gld.SetObject({"guild_id": str(ctx.guild.id)}, {
                        "currency.modif-by": person.name,
                        "currency.last-modified": datetime.datetime.now().strftime('%B %d %Y')
                        })
                    await ctx.send(embed=emb)

    # Others

    @staticmethod
    async def print_help(channel: discord.TextChannel):
        pref: str = get_prefix(channel.guild)
        emb = discord.Embed(
            title="💸 Currency Manager | Help",
            description="A custom server currency, set your chat money, set yout currency and "
                "use this money for several things like buy items, equipments, and learn moves.",
            colour=WHITE
            )
        emb.add_field(
            name="Command :",
            value=f"`{pref}cur <option>`",
            inline=False
            )
        emb.add_field(
            name="Options :",
            value="`-t <symbol>` - Set currency type in your server\n"
                "`-get` Get info about server currency\n"
                "`-min <amount>` - Set minimal getting money by chat\n"
                "`-max <amount>` - Set maximal getting money by chat",
            inline=False
            )
        emb.set_footer(text=f"Example Command : {pref}cur -get")
        await channel.send(embed=emb)

def setup(bot: commands.Bot):
    bot.add_cog(Currency(bot))