import discord
import asyncio
import time
from discord.ext import commands
from Settings.MyUtility import get_prefix

WHITE = 0xfffffe

class HelpCommand(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="help", aliases=['h'])
    async def _help(self, ctx: commands.Context, *args):
        """Custom Help Command."""
        pref: str = get_prefix(ctx.guild)
        emb = discord.Embed(
            title="📝 Help | Menu",
            description="Type prefix followed by one of these command. (To make this public in server instead, add space followed by `public` next to command)\n"
                    "> Note : don't use `public` in the server, this probably may cause spam and got blame for spam except if your server have a channel that able for spam.",
            colour=WHITE
            )
        emb.add_field(
            name="General Commands :", inline=False, 
            value="`ping` - PING. PONG!\n"
                "`about`|`a` - Bot information\n"
                "`news` - What's new?\n"
                "`help`|`h` - This help command\n"
                "`prefix`|`pfix` - Change prefix\n"
                "`feedback`|`fb` - Send message to creator\n"
                "`settitle`|`st` - Change profile title\n"
                "`prof`|`user` - User profile\n"
                "`img`|`pict` - Search picture\n"
                "`setevent <channel>` - Set all event into channel")
        emb.add_field(
            name="Fun and Game Commands :", inline=False, 
            value="`ask` - Ask me anything\n"
                "`chance` - Your chance of\n"
                "`choose` - Random chooser machine\n"
                "`duel` - Duel simulation\n"
                "`dice` - Roll the dice\n"
                "`dig`|`mine` - Mining is fun\n"
                "`hangman`|`hang` - Hangman game\n"
                "`ows` - One Word Story game\n"
                "`pool` - 8Pool says\n"
                "`rps` - Rock Paper Scissor\n"
                "`scramble`|`scr` - Guess scramble word\n"
                "`slot` - Slot machine\n"
                "`wordpref`|`wop` - Custom Word Prefix Game")
        emb.add_field(
            name="RPG Commands :", inline=False, 
            value="`start` - Getting started with RPG\n"
                "`adventure`|`adv` - Virtual adventure\n"
                "`battle`|`btl` - Battle multiplayer\n"
                "`close` - Close your progress\n"
                "`equip` - Managing equipment\n"
                "`item` - Managing item\n"
                "`learn` - Learn any moves in server\n"
                "`mymoves` - See your current moves\n"
                "`manual` - Manual all about this RPG\n"
                "`class` - Check classes available\n"
                "`nature` - Check Nature available\n"
                "`skilladd` - Upgrade your primary stat\n"
                "`skillres` - Reset your skill point\n"
                "`stat` - Your detail in RPG\n"
                "`create` - Create a custom thing")
        emb.add_field(
            name="Meta and Misc Commands :", inline=False, 
            value="`balance`|`bal` - Check yo money\n"
                "`buy` - Buy something in the shop\n"
                "`cur` - Manage server currency\n"
                "`inv` - Your inventory\n"
                "`leaderboard`|`lb` - Leaderboard in currency and RPG\n"
                "`ores`|`ore` - See your ore collection\n"
                "`shop` - Server shop and menu")
        emb.set_thumbnail(url=self.bot.user.avatar_url)
        emb.set_footer(text=f"Example Command : {pref}ping")
        if len(args) >= 1:
            if args[0].lower() == 'public':
                await ctx.send(embed=emb)
        else:
            await ctx.message.add_reaction("👍")
            await ctx.author.send(embed=emb)

def setup(bot: commands.Bot):
    bot.add_cog(HelpCommand(bot))