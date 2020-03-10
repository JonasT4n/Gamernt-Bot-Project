import discord
from discord.ext import commands, tasks
from Settings.Handler import *
import asyncio, random, os, threading
from Settings.DbManager import DbManager as dbm

WHITE = 0xfffffe

class UNO(commands.Cog):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.command(aliases=["Uno", "UNo", "UNO", "UnO", "uNO", "unO", "uNo"])
    async def uno(self, ctx, stat: str):
        statuses = ["start", "h", "help", "how"]
        try:
            if stat.lower() not in statuses:
                raise commands.BadArgument

            if stat.lower() == "help" or stat.lower() == "h": # Help
                emb = discord.Embed(colour=discord.Colour(WHITE))
                emb.set_author(name="~ Uno Game Card ~")
                emb.set_thumbnail(url="https://cdn.discordapp.com/attachments/588917150891114516/670457799955972096/UNO_MainCard.png")
                emb.add_field(name="Commands (alias)", value="""***Start*** *-> This will Start a New Game.*\n***Help (h)*** *-> Help about Uno Game Card.*\n***How*** *-> How to Play Uno.*""")
                emb.set_footer(text="Example Command : g.uno how")
                await ctx.send(embed=emb)

            if stat.lower() == "start": # Start New Game
                threading.Thread(target=await self.queuing(ctx)).start()
                
            if stat.lower() == "how": # How To Play UNO
                emb = discord.Embed(title="~ Uno Game Card ~", description="Draw a Card on top of it by Color, Number or Type.\n**Reverse** => If going clockwise, switch to counterclockwise. If going counterclockwise, switch to clockwise.\n**Skip** => When a player places this card, the next player has to skip their turn.\n**Wild** => This card represents all four colors, and can be placed on any card.\n**Wild Draw Four** => This acts just like the wild card except that the next player also has to draw four cards as well as forfeit his/her turn.\n**Draw Two** => When a person places this card, the next player will have to pick up two cards and forfeit his/her turn.", colour=discord.Colour(WHITE))
                emb.set_footer(text="Source from www.unorules.com")
                emb.set_thumbnail(url="https://cdn.discordapp.com/attachments/588917150891114516/670457799955972096/UNO_MainCard.png")
                await ctx.send(embed=emb)
                
        except Exception as exc:
            if type(exc) == commands.BadArgument:
                emb = discord.Embed(colour=discord.Colour(WHITE))
                emb.set_author(name="~ Uno Game Card ~")
                emb.set_thumbnail(url="https://cdn.discordapp.com/attachments/588917150891114516/670457799955972096/UNO_MainCard.png")
                emb.add_field(name="Commands (alias)", value="""***Start*** *-> This will Start a New Game.*\n***Help (h)*** *-> Help about Uno Game Card.*\n***How*** *-> How to Play Uno.*""")
                emb.set_footer(text="Example Command : g.uno how")
                await ctx.send(embed=emb)
            else:
                print(type(exc), exc)

    # Game Started, Initialize Everyone's Card and ChatBox Embed
    async def uno_gameplay(self, **datas):
        # What's in Datas : players=players -> [ppl]
        # Get Raw Materials
        connUnoData = dbm.connect_db("./DataPack/uno_game.db")
        connUnoData.SelectTableData("uno_raw")
        this_raw = connUnoData.cursor.fetchall()
        connUnoData.cursor.close()
        
        # Embed Picture Table
        members_card, players, host, dm_msg = {}, datas['players'], datas['channel_host'], {}
        unoTable = [None, random.choice(this_raw)]
        embed_display = discord.Embed(title="🎮 Uno Table", colour=discord.Colour(WHITE))
        embed_display.add_field(name="Previous Card \> Nothing", value="*First Card won't affect anyone*\n**v** Current Card on Top **v**")
        embed_display.set_image(url=unoTable[1][4])
        table_card = await host.send(embed=embed_display)
        
        # Initialize Each Member with Cards
        for ppl in players:
            if ppl.dm_channel is None:
                await ppl.create_dm()
            embed_private = discord.Embed(colour=discord.Colour(WHITE))
            deck = [random.choice(this_raw) for i in range(6)]
            deck_names = [str(this + 1) + '. ' + deck[this][3] for this in range(len(deck))]
            members_card[str(ppl.id)] = deck # String Id
            embed_private.add_field(name="Your Cards :", value="\n".join(deck_names))
            embed_private.set_footer(text="Draw Card by Sending a Number in the Server")
            dm_msg[str(ppl.id)] = await ppl.send(embed=embed_private)
        run, turn, tnc = True, 0, {"skip":False, "reversed":False, "stack":[False, 0]}
        
        # Gameplay Started
        while run:
            this_picked_card, dont_have = None, False
            try:
                whos_turn = await host.send(content="⏳ ***{}, Your Turn!*** ⏳".format(players[turn].name))
                if tnc["stack"][0] is True:
                    if not check_uno_stack(members_card[str(players[turn].id)]):
                        dont_have = True
                    else:
                        while True:
                            picked = await self.bot.wait_for(event="message", check=check_uno_pick_card(players[turn], members_card[str(players[turn].id)]), timeout=60.0)
                            if check_uno_match(unoTable[1], members_card[str(players[turn].id)][int(picked.content) - 1]) is False and members_card[str(players[turn].id)][int(picked.content) - 1][2] != "plus":
                                await picked.delete()
                                await whos_turn.edit(content="*That card can't be Draw,* ***Choose again {}***!".format(players[turn].name))
                                continue
                            else:
                                this_picked_card = members_card[str(players[turn].id)][int(picked.content) - 1]
                                del members_card[str(players[turn].id)][int(picked.content) - 1]
                                await picked.delete()
                                break
                else:
                    if check_uno_can_draw(unoTable[1], members_card[str(players[turn].id)]) is False:
                        dont_have = True
                    else:
                        while True:
                            picked = await self.bot.wait_for(event="message", check=check_uno_pick_card(players[turn], members_card[str(players[turn].id)]), timeout=60.0)
                            if not check_uno_match(unoTable[1], members_card[str(players[turn].id)][int(picked.content) - 1]):
                                await picked.delete()
                                await whos_turn.edit(content="*That card can't be Draw,* ***Choose again {}***!".format(players[turn].name))
                                continue
                            else:
                                this_picked_card = members_card[str(players[turn].id)][int(picked.content) - 1]
                                del members_card[str(players[turn].id)][int(picked.content) - 1]
                                await picked.delete()
                                break
            except Exception as exc:
                if type(exc) == asyncio.TimeoutError:
                    while True:
                        bot_pick_card_for_ya = random.choice(members_card[str(players[turn].id)])
                        await whos_turn.edit(content="Bot is Choosing for {}, everyone has been waiting for you.".format(players[turn].name))
                        if not check_uno_match(unoTable[1], bot_pick_card_for_ya):
                            continue
                        else:
                            this_picked_card = bot_pick_card_for_ya
                            members_card[str(players[turn].id)].remove(bot_pick_card_for_ya)
                            break
                else:
                    print(type(exc), exc)
            finally:
                this_new_embed = discord.Embed(colour=discord.Colour(WHITE))
                if dont_have is True: # Dont have a Card in current Player's Hand
                    if tnc["stack"][0] is True:
                        embed_display.set_footer(text="Stack Stopped, {} Takes {} Cards.".format(players[turn].name, tnc["stack"][1]))
                        while tnc["stack"][1] > 0:
                            members_card[str(players[turn].id)].append(random.choice(this_raw))
                            tnc["stack"][1] -= 1
                        tnc["stack"][0] = False
                    else:
                        embed_display.set_footer(text="{} don't have it and takes One Card".format(players[turn].name))
                    await table_card.edit(embed=embed_display)
                    members_card[str(players[turn].id)].append(random.choice(this_raw))
                else: # Have this Card
                    # Move Cards on Table
                    del unoTable[0]
                    unoTable.append(this_picked_card)
                    tnc = check_uno_card_effect(tnc, unoTable[1])
                    embed_display = discord.Embed(title="🎮 Uno Table", colour=discord.Colour(WHITE))
                    embed_display.add_field(name="{} has drawn {}".format(players[turn].name.split('#')[0], unoTable[1][3]), value="**v** Current Card on Top **v**")
                    embed_display.set_thumbnail(url=unoTable[0][4])
                    embed_display.set_image(url=unoTable[1][4])
                    await table_card.delete()
                    table_card = await host.send(embed=embed_display)
                    # Check Card Empty
                    if len(members_card[str(players[turn].id)]) == 0:
                        # Clear all Cache
                        run = False
                        await whos_turn.delete()
                        await table_card.delete()
                        for i in dm_msg:
                            await dm_msg[i].delete()
                        await self.announce_winner(players[turn], host, players, members_card)
                    else:
                        # Check if Stacked and the player doesn't do chain stack
                        if tnc["stack"][0] is True and unoTable[1][2] != "plus":
                            this_new_embed.set_footer(text="You've got {} Card(s) from Stack.".format(tnc["stack"][1]))
                            while tnc["stack"][1] > 0:
                                members_card[str(players[turn].id)].append(random.choice(this_raw))
                                tnc["stack"][1] -= 1
                            tnc["stack"][0] = False
                        # If the Player Drawn a Wild Card
                        if unoTable[1][1] == "black":
                            color_msg_handler = await host.send(content="*You've Drawn the Wild Card, now* ***Pick a Color!*** *[green, red, blue, yellow]*")
                            pick_color = None
                            try:
                                colors = ['green', 'blue', 'red', 'yellow']
                                pick_color = await self.bot.wait_for(event="message", check=uno_game_pick_color(players[turn]), timeout=80.0)
                                pick_color = pick_color.content.lower()
                            except Exception as exc:
                                if type(exc) == asyncio.TimeoutError:
                                    pick_color = random.choice(colors)
                            await color_msg_handler.delete()
                            unoTable[1] = (unoTable[1][0], pick_color, unoTable[1][2], unoTable[1][3], unoTable[1][4], unoTable[1][5], unoTable[1][6])
                            the_wild_color = await host.send(content="**The Wild Card color is {}**".format(pick_color))
                # Update Current Card Player Has
                deck_names = [str(card + 1) + '. ' + members_card[str(players[turn].id)][card][3] for card in range(len(members_card[str(players[turn].id)]))]
                this_new_embed.add_field(name="Your Cards :", value="\n".join(deck_names), inline=False)
                this_new_embed.set_footer(text="Draw Card by Sending a Number in the Server")
                await dm_msg[str(players[turn].id)].edit(embed=this_new_embed)
                # Check Turn
                turn, tnc = check_uno_person_turn(turn, tnc, len(players) - 1)
                # Replace Message Handler
                await whos_turn.delete()
                    
    async def announce_winner(self, winner, host, players, cards_left: dict):
        # Insert All Data in one Array
        all_cards_leftover = []
        for his_deck in range(len(cards_left)):
            all_cards_leftover.append([players[his_deck], len(cards_left[str(players[his_deck].id)])])
        # Insertion Sort
        for identity in range(len(all_cards_leftover)):
            temp_val = all_cards_leftover[identity]
            hole_pos = identity - 1
            while hole_pos >= 0 and all_cards_leftover[hole_pos][1] > temp_val[1]:
                all_cards_leftover[hole_pos + 1] = all_cards_leftover[hole_pos]
                hole_pos -= 1
            all_cards_leftover[hole_pos + 1] = temp_val
        # Make Display Embed
        emb_leaderboard = discord.Embed(title="~ Game Over ~", colour=discord.Colour(WHITE))
        emb_leaderboard.set_thumbnail(url="https://cdn.discordapp.com/attachments/588917150891114516/670457799955972096/UNO_MainCard.png")
        result = ''
        for identity in range(len(all_cards_leftover)):
            if identity == len(all_cards_leftover) - 1:
                result += "**{}.** {} => {} cards left.".format(identity + 1, all_cards_leftover[identity][0].name, all_cards_leftover[identity][1])
            elif identity == 0:
                result += "**{}.** {} The Winner!\n".format(identity + 1, all_cards_leftover[identity][0].name)
            else:
                result += "**{}.** {} => {} cards left.\n".format(identity + 1, all_cards_leftover[identity][0].name, all_cards_leftover[identity][1])
        emb_leaderboard.add_field(name="🏆 Congratulation {}! 🏆".format(winner.name), value="**Ranks :**\n{}".format(result))
        emb_leaderboard.set_footer(text="Some Players Earn Coins. Check it out!")
        await host.send(embed=emb_leaderboard)
        threading.Thread(target=self.earn_coins([ppl[0] for ppl in all_cards_leftover])).start()
    
    def earn_coins(self, players: list): # Earn Coins
        temp_conn = dbm.connect_db("./DataPack/member.db")
        for ppl in range(len(players)):
            temp_conn.cursor.execute("""SELECT * FROM point WHERE id=:uid""", {"uid":str(players[ppl].id)})
            get_user_info = temp_conn.cursor.fetchone()
            if ppl == 0:
                if get_user_info is None:
                    temp_conn.cursor.execute("""INSERT INTO point VALUES (:uid, :p)""", {"p":250, "uid":str(players[ppl].id)})
                else:
                    temp_conn.cursor.execute("""UPDATE point SET coins = coins + :p WHERE id=:uid""", {"p":250, "uid":str(players[ppl].id)})
            else:
                if get_user_info is None:
                    temp_conn.cursor.execute("""INSERT INTO point VALUES (:uid, :p)""", {"p":100, "uid":str(players[ppl].id)})
                else:
                    temp_conn.cursor.execute("""UPDATE point SET coins = coins + :p WHERE id=:uid""", {"p":100, "uid":str(players[ppl].id)})
        temp_conn.connect.commit()
        temp_conn.cursor.close()

    @uno.error
    async def uno_error(self, ctx, error):
        emb = discord.Embed(colour=discord.Colour(WHITE))
        if isinstance(error, commands.MissingRequiredArgument):
            emb.set_author(name="~ Uno Game Card ~")
            emb.set_thumbnail(url="https://cdn.discordapp.com/attachments/588917150891114516/670457799955972096/UNO_MainCard.png")
            emb.add_field(name="Commands (alias)", value="""***Start (UNDER MAINTENANCE)*** *-> This will Start a New Game.*\n***Help (h)*** *-> Help about Uno Game Card.*""")
            await ctx.send(embed=emb)

    async def queuing(self, ctx):
        # Making a Queue Embed Message
        emb = discord.Embed(colour=discord.Colour(WHITE))
        players = [ctx.message.author]
        listBoxer = "\n".join(["{}. ".format(ppl + 1) + players[ppl].name for ppl in range(len(players))])
        this_channel_id = ctx.message.channel.id
        waiting_player_session = True
        emb.add_field(name="🍺 Waiting for other to Join...", value="Current Players : {}/8\n{}".format(len(players), listBoxer))
        emb.set_footer(text="Type JOIN to Join in! Type SKIP to start without waiting it Full! The Game can be Start with 2-8 Players.")
        current_msg = await ctx.send(embed=emb)
        # Waiting for Player to Join
        try:
            while waiting_player_session:
                next_this_msg = await self.bot.wait_for(event="message", check=check_author_join_uno(this_channel_id), timeout=120.0)
                emb = discord.Embed(colour=discord.Colour(WHITE))
                if next_this_msg.content.lower() == "join" and next_this_msg.author not in players:
                    players.append(next_this_msg.author)
                    listBoxer = "\n".join(["{}. ".format(ppl + 1) + players[ppl].name for ppl in range(len(players))])
                    emb.add_field(name="🍺 Waiting for other to Join...", value="Current Players : {}/8\n{}".format(len(players), listBoxer))
                    emb.set_footer(text="Type JOIN to Join in! Type SKIP to start without waiting it Full! The Game can be Start with 2-8 Players.")
                    await current_msg.edit(embed=emb)
                    await next_this_msg.delete()
                if next_this_msg.content.lower() == "skip" and len(players) > 1 and next_this_msg.author in players:
                    await next_this_msg.delete()
                    waiting_player_session = False
                if len(players) == 8:
                    waiting_player_session = False
        except Exception as exc:
            if type(exc) == asyncio.TimeoutError:
                if len(players) < 2:
                    await ctx.send("❌ Request TimeOut! Please Try again in few Seconds.")
                    await current_msg.delete()
                else:
                    await ctx.send("Request TimeOut! {} Will you Start the Game Now or Cancel the Game? <**Start**, **Cancel**>".format(ctx.message.author.mention))
                    cons_msg = await self.bot.wait_for(event="message", check=check_author(ctx.message.author))
                    if cons_msg.content.lower() == "start":
                        await self.uno_gameplay(players=players, channel_host=ctx.message.channel)
                    else:
                        await current_msg.delete()
                        await ctx.send(content="Ok, Next Time!")
            else:
                print(type(exc), exc)
        else:
            await current_msg.edit(content="**Game will Start in few Seconds!**\nCheck your Cards in **DM**!")
            await self.uno_gameplay(players=players, channel_host=ctx.message.channel)

def setup(bot):
    bot.add_cog(UNO(bot))