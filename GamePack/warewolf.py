import discord
from discord.ext import commands
from Settings.Handler import *

WHITE = 0xfffffe

class WareWolf(commands.Cog):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.command(aliases=['ww'])
    async def warewolf(self, ctx, stat: str):
        statuses = ["start", "h", "help", "how"]
        try:
            if stat.lower() not in statuses:
                raise commands.BadArgument

            if stat.lower() == 'help' or stat.lower() == "h": # Help
                emb = discord.Embed(colour=discord.Colour(WHITE))
                emb.set_author(name="~ RPG Warewolf ~")
                emb.set_thumbnail(url="https://cdn.discordapp.com/attachments/588917150891114516/670585777238966292/warewolf.png")
                emb.add_field(name="Commands (alias)", value="***Start*** *-> This will Start a New Game.*\n***Help*** *-> Help about RPG Warewolf.*")
                emb.add_field(name="Example Command : g.warewolf how")
                await ctx.send(embed=emb)

            if stat.lower() == "start": # Start New Game
                emb = discord.Embed(title="COMING SOON!", colour=discord.Colour(WHITE))
                await ctx.send(embed==emb)
                
            if stat.lower() == "how": # How to Play Warewolf
                emb = discord.Embed(title="COMING SOON!", colour=discord.Colour(WHITE))
                await ctx.send(embed==emb)

        except Exception as exc:
            if type(exc) == commands.BadArgument:
                emb = discord.Embed(colour=discord.Colour(WHITE))
                emb.set_author(name="~ RPG Warewolf ~")
                emb.set_thumbnail(url="https://cdn.discordapp.com/attachments/588917150891114516/670585777238966292/warewolf.png")
                emb.add_field(name="Commands (alias)", value="***Start*** *-> This will Start a New Game.*\n***Help*** *-> Help about RPG Warewolf.*")
                emb.add_field(name="Example Command : g.warewolf how")
                await ctx.send(embed=emb)
            else:
                print(type(exc), exc)

    @warewolf.error
    async def ww_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            emb = discord.Embed(colour=discord.Colour(WHITE))
            emb.set_author(name="~ RPG Warewolf ~")
            emb.set_thumbnail(url="https://cdn.discordapp.com/attachments/588917150891114516/670585777238966292/warewolf.png")
            emb.add_field(name="Commands (alias)", value="***Start*** *-> This will Start a New Game.*\n***Help*** *-> Help about RPG Warewolf.*")
            await ctx.send(embed=emb)

def setup(bot):
    bot.add_cog(WareWolf(bot))