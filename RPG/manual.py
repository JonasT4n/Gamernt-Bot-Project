import discord
import asyncio
from discord.ext import commands
from Settings.MyUtility import get_prefix

WHITE = 0xfffffe

class RPGManual(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Command Area

    @commands.command(name= "manual")
    async def _manual(self, ctx: commands.Context, *, page: int = 1):
        # Inner Functions for Page Update
        # Page 1
        async def _page_one(message: discord.Message):
            pref: str = get_prefix(message.guild)
            emb = discord.Embed(
                title="Welcome Player!",
                description="To get started with this RPG, Use the `start` command."
                    "Use the command type prefix followed by the name of the command."
                    "`<prefix><command>`",
                colour=WHITE
                )
            emb.add_field(
                name="What is this bot anyway?",
                value="An RPG with Turn Base Battle which you can make your own `Moves`, your own `Equipment`, and your own `Items` to play around with."
                    "There's also some minigames and other cool stuff you want to explore :)",
                inline=False
                )
            emb.add_field(
                name="RPG Commands :",
                value="`start` - Getting started with RPG\n"
                    "`adventure`|`adv` - Virtual adventure\n"
                    "`battle`|`btl` - Battle multiplayer\n"
                    "`close` - Close your progress\n"
                    "`equip` - Managing equipment\n"
                    "`item` - Managing item\n"
                    "`learn` - Learn any moves in server\n"
                    "`moves` - See your current moves\n"
                    "`manual` - Manual all about this RPG\n"
                    "`class` - Check classes available\n"
                    "`nature` - Check Nature available\n"
                    "`skilladd` - Upgrade your primary stat\n"
                    "`skillres` - Reset your skill point\n"
                    "`stat` - Your detail in RPG",
                inline=False
                )
            await message.edit(embed=emb)

        # Page 2
        async def _page_two(message: discord.Message):
            pref: str = get_prefix(message.guild)
            emb = discord.Embed(
                title="RPG User Stat",
                description="After you have made your character, you can see your stat profile with `stat` command. "
                    "This is Optional : You can close your progress with `close` command, but it will completely deleted your currents. ",
                colour=WHITE
                )
            emb.add_field(
                name="What's in your Stat?",
                value="`LVL` & `EXP` - Your Experience with RPG\n"
                    "`SP` - Your Skill Point(s)\n"
                    "`CLASS` - Which class and nature you are in.\n"
                    "`Skill Stat` - Your skills to improve your character Substat\n"
                    "`Substat` - This will be use in the battlefield to show how strong you are",
                inline=False
                )
            emb.add_field(
                name="How to improve my character?",
                value="You can improve your stats if you have `SP` (Skill Points). Each time you leveled up, you will gain 1 SP to upgrade your Stat. "
                    "To level up your character, you can `battle` with others and `chat` in server if the bot is in the server. "
                    "Use `SP` with `skilladd` command.",
                inline=False
                )
            await message.edit(embed= emb)

        # Page 3
        async def _page_three(message: discord.Message):
            pref: str = get_prefix(message.guild)
            emb = discord.Embed(
                title="Skills and Substats",
                description="These skills will improve much for your character substat which will be used for `battle`.",
                colour=WHITE
                )
            emb.add_field(
                name="Skill (alias) :",
                value="`Strength` (`STR`) - Improves Attack. Big muscles kill your enemy.\n"
                    "`Endurance` (`END`) - Improves Hitpoint. You can stay longer in the arena.\n"
                    "`Agility` (`AGI`) - Improves Speed. Who's faster will get the first turn.\n"
                    "`Focus` (`FOC`) - Improves Critical Chance of any Attack type.\n"
                    "`Intelligence` (`ITE`) - Improves Magic Attack. Smarter to use spells at your enemy.\n"
                    "`Wise` (`WIS`) - Improves Defend against Magic.",
                inline=False
                )
            await message.edit(embed=emb)

        # Main
        try:
            list_of_page: list = [_page_one, _page_two, _page_three]
            menus: list = ["⏮️", "⬅️", "⏹", "➡️"]
            hm: discord.Message = await ctx.send(embed=discord.Embed(colour=WHITE))
            await list_of_page[page - 1](hm)
            for i in menus:
                await hm.add_reaction(i)
            while True:
                react: discord.Reaction
                user: discord.User
                react, user = await self.bot.wait_for(
                    event="reaction_add",
                    check=lambda r, u: True if str(r.emoji) in menus and u == ctx.author else False,
                    timeout=30.0
                    )

                # Page Counting
                if str(react.emoji) == "➡️":
                    if page == len(list_of_page):
                        continue
                    else:
                        page += 1
                elif str(react.emoji) == "⬅️":
                    if page == 1:
                        continue
                    else:
                        page -= 1
                elif str(react.emoji) == "⏮️":
                    if page == 1:
                        continue
                    else:
                        page = 1
                else:
                    raise asyncio.TimeoutError

                # Get Content and Update Message
                await react.remove(user)
                await list_of_page[page - 1](hm)
        except asyncio.TimeoutError:
            for j in menus:
                await hm.remove_reaction(j, ctx.me)

def setup(bot: commands.Bot):
    bot.add_cog(RPGManual(bot))