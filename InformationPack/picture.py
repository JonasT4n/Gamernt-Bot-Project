import discord
import sys
import os
import asyncio
from googleapiclient.discovery import build
from discord.ext import commands
from Settings.MyUtility import get_prefix
from Settings.StaticData import GOOGLE_API, CSE_ID

WHITE = 0xfffffe

class Picture(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.srv = build("customsearch", "v1", developerKey=GOOGLE_API).cse()

    # Command Area

    @commands.command(name="picture", aliases=["pict", "img"])
    async def _pict(self, ctx: commands.Context, *args):
        if len(args) == 0:
            await ctx.send(content= f"**Insert your argument.**\nExample Command : {get_prefix(ctx.guild.id)}img Maldives")
        else:
            # Connect with Google Custom Search
            async with ctx.typing():
                search_term: str = " ".join(args)
                response = self.srv.list(
                    q=search_term,
                    cx=CSE_ID,
                    searchType="image",
                    num=10,
                    fileType='jpg,jpeg,png',
                    safe='active'
                    ).execute()
                index: int = 0
                max_index = len(response["items"])
                link_url: list = [i["link"] for i in response["items"]]

            # Initiate Embed
            menus: list = ["⏮️", "⬅️", "⏹", "➡️"]
            emb = discord.Embed(
                title=f"Search Picture | Image : {index + 1}/{max_index}",
                description=f"Searching for {search_term}, Result ({max_index} Entries) : ",
                colour=WHITE)
            emb.set_image(url=link_url[index])
            emb.set_footer(text=f"Image : {index + 1}/{max_index} | Searched by {ctx.author.nick if ctx.author.nick is not None else ctx.author.name}")
            hm: discord.Message = await ctx.send(embed=emb)
            for i in menus:
                await hm.add_reaction(i)
            try:
                r: discord.Reaction
                u: discord.User
                while True:
                    r, u = await self.bot.wait_for(event= "reaction_add", timeout= 30.0,
                        check= lambda reaction, user: True if str(reaction.emoji) in menus and user == ctx.author else False)
                    if str(r.emoji) == "⏮️":
                        if index == 0:
                            continue
                        else:
                            index = 0
                    elif str(r.emoji) == "⬅️":
                        if index > 0:
                            index -= 1
                        else:
                            continue
                    elif str(r.emoji) == "⏹":
                        emb = discord.Embed(title=f"Search Picture | Image : {index + 1}/{max_index}",
                            description=f"Searching for {search_term}, Result ({max_index} Entries) : ",
                            colour=WHITE)
                        emb.set_image(url=link_url[index])
                        emb.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
                        await r.remove(u)
                        await hm.edit(embed=emb)
                        for j in menus:
                            await hm.remove_reaction(j, ctx.me)
                        return
                    else:
                        if index < max_index - 1:
                            index += 1
                        else:
                            continue
                    emb = discord.Embed(
                        title=f"Search Picture | Image : {index + 1}/{max_index}",
                        description=f"Searching for {search_term}, Result ({max_index} Entries) : ",
                        colour=WHITE)
                    emb.set_image(url=link_url[index])
                    emb.set_footer(text=f"Searched by {ctx.author.nick if ctx.author.nick is not None else ctx.author.name}")
                    await r.remove(u)
                    await hm.edit(embed=emb)
            except asyncio.TimeoutError:
                emb.set_footer(text=f"Searched by {ctx.author.nick if ctx.author.nick is not None else ctx.author.name} | Request Timeout")
                await hm.edit(embed=emb)
                for j in menus:
                    await hm.remove_reaction(j, ctx.me)

def setup(bot : commands.Bot):
    bot.add_cog(Picture(bot))