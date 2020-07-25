import discord
import asyncio
import re
from discord.ext import commands
from Settings.MyUtility import checkin_guild, checkin_member, db_gld, db_mbr, is_number, get_prefix, checkClassID
from RPGPackage.RPGElemental import TYPE_ELEMENT
from RPGPackage.RPGEquipment import eq_structure
from RPGPackage.RPGMovement import move_structure, TYPE_ATTACK, TYPE_TARGET

WHITE = 0xfffffe

def embed_move_maker(struct: dict):
    emb = discord.Embed(title="🏃 No Name" if len(struct["NAME"]) == 0 else f"🏃 {struct['NAME']}", colour=WHITE)
    emb.add_field(name="Type Attack", 
        value="Unidentified" if struct["TYPE_ATT"] is None else TYPE_ATTACK[struct["TYPE_ATT"]],
        inline=False)
    emb.add_field(name="Element",
        value="Unidentified" if struct["ELEMENT"] is None else TYPE_ELEMENT[struct["ELEMENT"]],
        inline=False)
    emb.add_field(name="Target",
        value="Unidentified" if struct["TARGET"] is None else TYPE_TARGET[struct["TARGET"]],
        inline=False)
    emb.add_field(name="Attack Message",
        value="Doing Nothing" if struct["ATTMSG"] is None else struct["ATTMSG"],
        inline=False)
    emb.add_field(name="Required Mana",
        value="<number>" if struct["MANA"] is None else struct["MANA"],
        inline=False)
    return emb

class RPGManager(commands.Cog):

    # Cog Constructor
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Commands Area
    # This item command allows the user to see his/her items in backpack.
    # Either user can manage himself/herself to insert or delete it.
    @commands.command(name="myitem", aliases=['myitems'])
    async def _my_item(self, ctx: commands.Context):
        pass

    # This equip command allows the user to see his/her current equipped things.
    @commands.command(name="myequip")
    async def _my_equipment(self, ctx: commands.Context):
        pass
    
    # This move command allows the user to see what have user learned from the server.
    # Moves is automatically saved into user identity
    @commands.command(name="mymoves", aliases=["learned"])
    async def _learned_moves(self, ctx: commands.Context):
        mbr_data = checkin_member(ctx.author)
        if mbr_data is not None:
            if "moves" in mbr_data:
                char_player = checkClassID(ctx.author)
                emb = discord.Embed(title=f"{char_player.name} Move")
                normal_detail: dict = char_player._normal_move.GetDetail
                custom_detail: list = [n.GetDetail for n in char_player._custom_moves]
                emb = discord.Embed(title="Learned Moves", colour=WHITE)
                emb.add_field(name=f"Normal Move: {normal_detail['Name']}", inline=False, 
                    value=f"Type Attack: {normal_detail['Type Attack'][1]}\n"
                        f"Element: {normal_detail['Element'][1]}\n"
                        f"Target: {normal_detail['Target'][1]}\n"
                        f"Required Mana: {normal_detail['Required Mana']}")
                for i in range(len(custom_detail)):
                    emb.add_field(name=f"Custom Move {i+1}: {custom_detail[i]['Name']}", inline=False, 
                        value=f"Type Attack: {custom_detail[i]['Type Attack'][1]}\n"
                            f"Element: {custom_detail[i]['Element'][1]}\n"
                            f"Target: {custom_detail[i]['Target'][1]}\n"
                            f"Required Mana: {custom_detail[i]['Required Mana']}")
                await ctx.send(embed=emb)
            else:
                await ctx.send(f"__**{ctx.author.name}, You haven't start your character, type {get_prefix(ctx.guild)}start to begin.**__")

    # Learn things from guild if guild haas made some custom moves
    @commands.command(name="learn", aliases=["moves"])
    async def _learn(self, ctx: commands.Context, page: int = 1):
        mbr_data = checkin_member(ctx.author)
        if mbr_data is not None:
            if "moves" in mbr_data:
                if len(mbr_data["moves"]) < 3:
                    gld_data = checkin_guild(ctx.guild)
                    # No Moves Available
                    if len(gld_data["shop"]["movements"]) == 0:
                        emb = discord.Embed(title=f"No Moves Available in {ctx.guild.name}", 
                            description=f"Create your first custom move, type `{get_prefix(ctx.guild)}create move` to make it up.", colour=WHITE)
                        await ctx.send(embed=emb)
                    # There are moves in the guild
                    else:
                        move_data: list = gld_data["shop"]["movements"]
                        menu = ["⬅️", "✅", "🚫", "➡️"]
                        emb = embed_move_maker(move_data[page - 1])
                        emb.set_footer(text="React with ✅ to learn this Move or 🚫 to abort.")
                        hm: discord.Message = await ctx.send(embed=emb)
                        for i in menu:
                            await hm.add_reaction(i)
                        try:
                            while True:
                                r, u = await self.bot.wait_for(event="reaction_add", timeout=30.0, 
                                                               check=lambda reaction, user: True if str(reaction.emoji) in menu and user == ctx.author else False)
                                await hm.remove_reaction(str(r.emoji), u)
                                # Accept Training
                                if str(r.emoji) == "✅":
                                    for j in menu:
                                        await hm.remove_reaction(j, ctx.me)
                                    db_mbr.UpdateObject({"member_id": str(ctx.author.id)}, {"$push": {"moves": move_data[page - 1]}})
                                    await hm.edit(content=f"{ctx.author.mention} learned `{move_data[page - 1]['NAME']}`.")
                                    break
                                # Abort Training
                                elif str(r.emoji) == "🚫":
                                    await hm.edit(content="*Action Aborted*")
                                    break
                                # Next Page
                                elif str(r.emoji) == "➡️":
                                    page = page + 1 if page < len(move_data) else 1
                                # Previous Page
                                elif str(r.emoji) == "⬅️":
                                    page = page - 1 if page > 0 else len(move_data)
                                # Edit Message Input
                                emb = embed_move_maker(move_data[page - 1])
                                emb.set_footer(text="React with ✅ to learn this Move or 🚫 to abort.")
                                await hm.edit(embed=emb)
                        except asyncio.TimeoutError:
                            await hm.edit(content="*Request Timeout*")
            else:
                await ctx.send(f"__**{ctx.author.name}, You haven't start your character, type {get_prefix(ctx.guild)}start to begin.**__")

    # Make Custom Things like Equipment, Item, or Movement
    # This is the main Command
    @commands.command(name="create")
    async def _make_things(self, ctx: commands.Context, *args):
        """## Arguments
        ------------
        Insert with the following order: `option`(str) `name`(str). It is optional.

        ## Options
        ----------
        Move, Item, Equipment
        """
        mbr_data = checkin_member(ctx.author)
        if mbr_data is not None:
            if "moves" in mbr_data:
                if len(args) == 0:
                    await self.__creator_help(ctx.channel)
                elif len(args) >= 1:
                    gld_data: dict = checkin_guild(ctx.guild)
                    if args[0].lower() == "move" or args[0].lower() == "m":
                        if len(gld_data["shop"]["movements"]) >= gld_data["max-misc"]["move"]:
                            await ctx.send("Server already contain full Custom Move. You can't create unless delete one of them.")
                        else:
                            await self.__make_move_process(ctx.channel, ctx.author, name=" ".join(args[1:]))
                    elif args[0].lower() == "item" or args[0].lower() == "i":
                        if len(gld_data["shop"]["equipments"]) >= gld_data["max-misc"]["equip"]:
                            await ctx.send("Server already contain full Custom Move. You can't create unless delete one of them.")
                        else:
                            await self.__make_item_process(ctx.channel, ctx.author, name=" ".join(args[1:]))
                    elif args[0].lower() == "equipment" or args[0].lower() == "eq":
                        if len(gld_data["shop"]["items"]) >= gld_data["max-misc"]["item"]:
                            await ctx.send("Server already contain full Custom Move. You can't create unless delete one of them.")
                        else:
                            await self.__make_eq_process(ctx.channel, ctx.author, name=" ".join(args[1:]))
            else:
                await ctx.send(f"__**{ctx.author.name}, You haven't start your character, type {get_prefix(ctx.guild)}start to begin.**__")

    # Processor Area
    # Making a custom move processor
    async def __make_move_process(self, channel: discord.TextChannel, person: discord.User, *, name = ""):
        """Asynchronously request for detail."""
        # Inner Functions
        # Check User Inputs
        # Check Input Type Attack
        def check_type_att(content: str):
            if is_number(content):
                if int(content) in TYPE_ATTACK:
                    return True
            return False

        # Check Input Element Type
        def check_type_element(content: str):
            if is_number(content):
                if int(content) in TYPE_ELEMENT:
                    return True
            return False

        # Check Input Target Type
        def check_type_target(content: str):
            if is_number(content):
                if int(content) in TYPE_TARGET:
                    return True
            return False

        # Remove unnecessary information, for custom name and custom message
        # Any User tag will be removed from string
        def check_reply_content(content: str):
            tags = re.findall(r"<@!\d+>", content)
            if len(tags) > 0:
                for tag in tags:
                    user: discord.User = self.bot.get_user(int(tag.split('!')[1][:-1]))
                    if user is not None:
                        content = content.replace(tag, user.name)
                    else:
                        content = content.replace(tag, "null")
            return content

        new_move_structure: dict = move_structure
        new_move_structure["NAME"] = check_reply_content(name)
        hm: discord.Message = await channel.send(content="Insert the name of this movement, send a message with any name." if len(name) == 0 \
            else "Insert Type Attack, send a message with number.\n[1=`Physical`, 2=`Magic`]", embed=embed_move_maker(new_move_structure))
        try:
            # if name not settled yet then request for name of move
            if len(name) == 0:
                rep: discord.Message = await self.bot.wait_for(event="message", timeout=40.0,
                    check=lambda message: True if channel == message.channel and person == message.author else False)
                new_move_structure["NAME"] = check_reply_content(rep.content)
                await rep.delete()
                await hm.edit(content="Insert Type Attack, send a message with number.\n[1=`Physical`, 2=`Magic`]", 
                    embed=embed_move_maker(new_move_structure))

            # Ask for Type Attack
            rep: discord.Message = await self.bot.wait_for(event="message", timeout=40.0,
                check=lambda message: True if channel == message.channel and person == message.author and check_type_att(message.content) else False)
            new_move_structure["TYPE_ATT"] = int(rep.content)
            await rep.delete()
            await hm.edit(content="Insert Element Type, send a message with number.\n[1=`Fire`; 2=`Water`; 3=`Earth`; 4=`Air`]", 
                embed=embed_move_maker(new_move_structure))

            # Ask for Element Type
            rep: discord.Message = await self.bot.wait_for(event="message", timeout=40.0,
                check=lambda message: True if channel == message.channel and person == message.author and check_type_element(message.content) else False)
            new_move_structure["ELEMENT"] = int(rep.content)
            await rep.delete()
            await hm.edit(content="Insert Element Type, send a message with number.\n[1=`Single Target`; 2=`Splash`]", 
                embed=embed_move_maker(new_move_structure))

            # Ask for Target Type
            rep: discord.Message = await self.bot.wait_for(event="message", timeout=40.0,
                check=lambda message: True if channel == message.channel and person == message.author and check_type_target(message.content) else False)
            new_move_structure["TARGET"] = int(rep.content)
            await rep.delete()
            await hm.edit(content="Insert message attack, this will trigger when you have used this move in battlefield."
                "You can add **<me>** as the user and **<enemy>** as the target enemy in the message. Send a message with any/multiple words.", 
                embed=embed_move_maker(new_move_structure))

            # Ask for use Message
            rep: discord.Message = await self.bot.wait_for(event="message", timeout=40.0,
                check=lambda message: True if channel == message.channel and person == message.author else False)
            new_move_structure["ATTMSG"] = check_reply_content(rep.content)
            await rep.delete()
            await hm.edit(content="Insert required mana to use this move, you can set it to 0. Send a message with number.", 
                embed=embed_move_maker(new_move_structure))

            # Ask for required Mana amount
            rep: discord.Message = await self.bot.wait_for(event="message", timeout=40.0,
                check=lambda message: True if channel == message.channel and person == message.author and is_number(message.content) else False)
            new_move_structure["MANA"] = int(rep.content)
            await rep.delete()
            await hm.edit(content=f"Result! made by {person.name}. use command {get_prefix(channel.guild)}learn to learn a new move in this server.", 
                embed=embed_move_maker(new_move_structure))

            # Save Move Data into database
            db_gld.UpdateObject({"guild_id": str(channel.guild.id)}, {"$push": {"shop.movements": new_move_structure}})
        except asyncio.TimeoutError:
            await hm.edit(content="Request Timeout! Creating Move has been cancelled.")

    # Making a custom item processor
    async def __make_item_process(self, channel: discord.TextChannel, person: discord.User, *, name = ""):
        """Asynchronously request for detail."""
        pass

    # Making a custom equipment processor
    async def __make_eq_proces(self, channel: discord.TextChannel, person: discord.User, *, name = ""):
        """Asynchronously request for detail."""
        pass

    # If you need a help about creating stuff
    async def __creator_help(self, channel: discord.TextChannel):
        pref: str = get_prefix(channel.guild)
        emb = discord.Embed(title="🗡️ Create Stuff | Help", colour=WHITE)
        emb.add_field(name="Command :", 
            value=f"> `{pref}create <option> [anyname]`",
            inline=False)
        emb.add_field(
            name="Options :",
            value="`move`|`m` - Custom move\n"
                "`item`|`i` - Custom item\n"
                "`equipment`|`eq` - Custom equipment",
            inline=False)
        emb.set_footer(text=f"Example command to create a custom move: {pref}create move Fireball with Spaghetti")
        await channel.send(embed=emb)

def setup(bot: commands.Bot):
    bot.add_cog(RPGManager(bot))